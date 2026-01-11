"""
GitHub API Module for Repository Explorer
Handles fetching repository structure and raw file contents.
"""
import re
import requests
import io
from typing import Optional, Tuple, List, Dict, Any
from urllib.parse import urlparse
import streamlit as st


class GitHubAPI:
    """Handles GitHub API interactions for repository exploration."""
    
    BASE_API_URL = "https://api.github.com"
    RAW_CONTENT_URL = "https://raw.githubusercontent.com"
    
    @staticmethod
    def parse_github_url(url: str) -> Optional[Dict[str, str]]:
        """
        Parse a GitHub URL to extract owner, repo, branch, and path.
        
        Supports formats:
        - https://github.com/owner/repo
        - https://github.com/owner/repo/tree/branch
        - https://github.com/owner/repo/tree/branch/path/to/folder
        - https://github.com/owner/repo/blob/branch/path/to/file
        
        Returns:
            dict with 'owner', 'repo', 'branch', 'path' or None if invalid
        """
        try:
            # Clean up URL
            url = url.strip().rstrip('/')
            
            # Handle various GitHub URL formats
            patterns = [
                # https://github.com/owner/repo/tree/branch/path
                r'github\.com/([^/]+)/([^/]+)/tree/([^/]+)(?:/(.+))?',
                # https://github.com/owner/repo/blob/branch/path
                r'github\.com/([^/]+)/([^/]+)/blob/([^/]+)(?:/(.+))?',
                # https://github.com/owner/repo (root)
                r'github\.com/([^/]+)/([^/]+)/?$',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    groups = match.groups()
                    return {
                        'owner': groups[0],
                        'repo': groups[1].replace('.git', ''),
                        'branch': groups[2] if len(groups) > 2 and groups[2] else 'main',
                        'path': groups[3] if len(groups) > 3 and groups[3] else ''
                    }
            
            return None
            
        except Exception:
            return None
    
    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def fetch_default_branch(owner: str, repo: str, token: Optional[str] = None) -> str:
        """Fetch the default branch of a repository. Cached for 1 hour."""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        url = f"{GitHubAPI.BASE_API_URL}/repos/{owner}/{repo}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get('default_branch', 'main')
        except Exception:
            return 'main'
    
    @staticmethod
    @st.cache_data(ttl=1800, show_spinner=False)
    def fetch_repo_tree(
        owner: str, 
        repo: str, 
        branch: str = "main", 
        token: Optional[str] = None
    ) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Fetch the complete file tree of a repository using GitHub Trees API.
        Cached for 30 minutes.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name (default: main)
            token: Optional GitHub personal access token
            
        Returns:
            Tuple of (tree_list, error_message)
            tree_list contains dicts with 'path', 'type', 'size', 'sha'
        """
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # Use the Trees API with recursive flag
        url = f"{GitHubAPI.BASE_API_URL}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            # Handle rate limiting
            if response.status_code == 403:
                remaining = response.headers.get('X-RateLimit-Remaining', '0')
                if remaining == '0':
                    return None, "GitHub API rate limit exceeded. Please provide a token or wait."
                return None, "Access forbidden. Repository may be private."
            
            # Handle not found
            if response.status_code == 404:
                return None, f"Repository or branch not found: {owner}/{repo}@{branch}"
            
            response.raise_for_status()
            data = response.json()
            
            # Check if tree is truncated (very large repos)
            if data.get('truncated', False):
                return data.get('tree', []), "Warning: Tree was truncated due to size. Some files may be missing."
            
            return data.get('tree', []), None
            
        except requests.exceptions.Timeout:
            return None, "Request timed out. Please try again."
        except requests.exceptions.HTTPError as e:
            return None, f"HTTP Error: {str(e)}"
        except Exception as e:
            return None, f"Error fetching repository: {str(e)}"
    
    @staticmethod
    def build_tree_structure(flat_tree: List[Dict]) -> List[Dict]:
        """
        Convert flat tree API response into hierarchical structure for UI.
        
        Args:
            flat_tree: List of items from GitHub Trees API
            
        Returns:
            List of root-level items with nested 'children' for folders
        """
        # Filter to only files and directories (blobs and trees)
        items = [
            {
                'path': item['path'],
                'type': 'folder' if item['type'] == 'tree' else 'file',
                'size': item.get('size', 0),
                'sha': item.get('sha', '')
            }
            for item in flat_tree
            if item['type'] in ('blob', 'tree')
        ]
        
        # Build nested structure
        root = []
        nodes = {}
        
        # Sort by path to ensure parents are processed first
        items.sort(key=lambda x: x['path'])
        
        for item in items:
            path = item['path']
            parts = path.split('/')
            name = parts[-1]
            
            node = {
                'label': name,
                'value': path,
                'type': item['type'],
                'size': item['size']
            }
            
            if item['type'] == 'folder':
                node['children'] = []
            
            nodes[path] = node
            
            if len(parts) == 1:
                # Root level item
                root.append(node)
            else:
                # Find parent folder
                parent_path = '/'.join(parts[:-1])
                if parent_path in nodes:
                    nodes[parent_path]['children'].append(node)
                else:
                    # Parent doesn't exist (shouldn't happen with sorted input)
                    root.append(node)
        
        return root
    
    @staticmethod
    def get_tree_select_nodes(tree_structure: List[Dict]) -> List[Dict]:
        """
        Convert tree structure to format expected by streamlit-tree-select.
        
        Returns list of dicts with 'label', 'value', and optional 'children'.
        """
        def convert_node(node: Dict) -> Dict:
            result = {
                'label': f"📁 {node['label']}" if node['type'] == 'folder' else f"📄 {node['label']}",
                'value': node['value']
            }
            if 'children' in node and node['children']:
                result['children'] = [convert_node(child) for child in node['children']]
            return result
        
        return [convert_node(node) for node in tree_structure]
    
    @staticmethod
    def fetch_raw_file(
        owner: str, 
        repo: str, 
        path: str, 
        branch: str = "main",
        token: Optional[str] = None
    ) -> Tuple[Optional[io.BytesIO], Optional[str]]:
        """
        Fetch raw file content from a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path within the repository
            branch: Branch name
            token: Optional GitHub token
            
        Returns:
            Tuple of (BytesIO file object, error_message)
        """
        # Use raw.githubusercontent.com for file content
        url = f"{GitHubAPI.RAW_CONTENT_URL}/{owner}/{repo}/{branch}/{path}"
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 404:
                return None, f"File not found: {path}"
            
            response.raise_for_status()
            
            # Create BytesIO object with the content
            file_obj = io.BytesIO(response.content)
            file_obj.name = path.split('/')[-1]  # Use just the filename
            
            return file_obj, None
            
        except requests.exceptions.Timeout:
            return None, f"Timeout fetching {path}"
        except Exception as e:
            return None, f"Error fetching {path}: {str(e)}"
    
    @staticmethod
    def fetch_multiple_files(
        owner: str,
        repo: str,
        paths: List[str],
        branch: str = "main",
        token: Optional[str] = None,
        progress_callback = None,
        repo_prefix: str = ""
    ) -> Tuple[List[io.BytesIO], List[str]]:
        """
        Fetch multiple files from a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            paths: List of file paths to fetch
            branch: Branch name
            token: Optional GitHub token
            progress_callback: Optional callback(current, total) for progress updates
            repo_prefix: Optional prefix for filenames to avoid conflicts
            
        Returns:
            Tuple of (list of file objects, list of error messages)
        """
        files = []
        errors = []
        total = len(paths)
        
        for i, path in enumerate(paths):
            file_obj, error = GitHubAPI.fetch_raw_file(owner, repo, path, branch, token)
            
            # Update progress after fetch completes
            if progress_callback:
                progress_callback(i + 1, total)
            
            if file_obj:
                # Add repo prefix to avoid filename conflicts
                if repo_prefix:
                    original_name = file_obj.name
                    file_obj.name = f"{repo_prefix}_{original_name}"
                files.append(file_obj)
            else:
                errors.append(error or f"Unknown error for {path}")
        
        return files, errors
    
    # --- Gist Support ---
    
    @staticmethod
    def parse_gist_url(url: str) -> Optional[str]:
        """
        Parse a Gist URL to extract the Gist ID.
        
        Supports:
        - https://gist.github.com/username/gist_id
        - https://gist.github.com/gist_id
        
        Returns:
            Gist ID or None if invalid
        """
        try:
            url = url.strip().rstrip('/')
            patterns = [
                r'gist\.github\.com/[^/]+/([a-f0-9]+)',
                r'gist\.github\.com/([a-f0-9]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            return None
        except Exception:
            return None
    
    @staticmethod
    @st.cache_data(ttl=1800, show_spinner=False)
    def fetch_gist(gist_id: str, token: Optional[str] = None) -> Tuple[Optional[List[io.BytesIO]], Optional[str]]:
        """
        Fetch all files from a GitHub Gist. Cached for 30 minutes.
        
        Returns:
            Tuple of (list of file BytesIO objects, error_message)
        """
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        url = f"{GitHubAPI.BASE_API_URL}/gists/{gist_id}"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 404:
                return None, "Gist not found. Check the URL or ensure it's public."
            
            response.raise_for_status()
            data = response.json()
            
            files = []
            for filename, file_info in data.get('files', {}).items():
                content = file_info.get('content', '')
                file_obj = io.BytesIO(content.encode('utf-8'))
                file_obj.name = filename
                files.append(file_obj)
            
            if not files:
                return None, "Gist contains no files."
            
            return files, None
            
        except Exception as e:
            return None, f"Error fetching Gist: {str(e)}"


# --- Folder Filter Presets ---
FILTER_PRESETS = {
    "exclude_common": {
        "name": "Exclude Common Dirs",
        "description": "node_modules, venv, __pycache__, .git, etc.",
        "exclude_dirs": [
            "node_modules", "venv", ".venv", "env", ".env",
            "__pycache__", ".git", ".svn", ".hg",
            "dist", "build", ".next", ".nuxt",
            "coverage", ".nyc_output", ".pytest_cache",
            "vendor", "packages", ".idea", ".vscode"
        ]
    },
    "source_only": {
        "name": "Source Files Only",
        "description": "Only code files, no configs/docs",
        "include_extensions": [
            ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h",
            ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala",
            ".vue", ".svelte", ".html", ".css", ".scss", ".sass", ".less"
        ]
    }
}


def apply_tree_filters(
    tree: List[Dict],
    exclude_dirs: List[str] = None,
    include_extensions: List[str] = None,
    exclude_extensions: List[str] = None,
    custom_exclude_patterns: List[str] = None
) -> List[Dict]:
    """
    Filter a flat tree list based on various criteria.
    
    Args:
        tree: Flat list from GitHub Trees API
        exclude_dirs: Directory names to exclude
        include_extensions: If provided, only include files with these extensions
        exclude_extensions: Extensions to exclude
        custom_exclude_patterns: Custom patterns to exclude (simple substring match)
    
    Returns:
        Filtered tree list
    """
    filtered = []
    
    exclude_dirs = set(exclude_dirs or [])
    include_extensions = set(ext.lower() for ext in (include_extensions or []))
    exclude_extensions = set(ext.lower() for ext in (exclude_extensions or []))
    custom_exclude_patterns = custom_exclude_patterns or []
    
    for item in tree:
        path = item.get('path', '')
        item_type = item.get('type', '')
        
        # Check if path contains an excluded directory
        path_parts = path.split('/')
        if any(part in exclude_dirs for part in path_parts):
            continue
        
        # Check custom exclude patterns
        if any(pattern in path for pattern in custom_exclude_patterns):
            continue
        
        # For files, check extensions
        if item_type == 'blob':
            filename = path_parts[-1]
            # Get extension (handle files without extensions like Dockerfile)
            if '.' in filename:
                ext = '.' + filename.rsplit('.', 1)[-1].lower()
            else:
                ext = ''
            
            # If include_extensions specified, check if file matches
            if include_extensions:
                # Allow files with matching extensions OR known extensionless files
                if ext:
                    if ext not in include_extensions:
                        continue
                else:
                    # No extension - check if it's a known file type
                    if not is_likely_file(path):
                        continue
            
            # Exclude specific extensions
            if ext and ext in exclude_extensions:
                continue
        
        filtered.append(item)
    
    return filtered


def is_likely_file(path: str) -> bool:
    """
    Determine if a path is likely a file (vs folder).
    Handles extensionless files like Dockerfile, Makefile, LICENSE.
    """
    filename = path.split('/')[-1]
    
    # Known extensionless files
    known_files = {
        'Dockerfile', 'Makefile', 'LICENSE', 'README', 'CHANGELOG',
        'Procfile', 'Gemfile', 'Rakefile', 'Vagrantfile', 'Brewfile',
        '.gitignore', '.gitattributes', '.dockerignore', '.editorconfig',
        '.env', '.env.example', '.env.local', 'Pipfile', 'Podfile'
    }
    
    if filename in known_files:
        return True
    
    # Has extension = file
    if '.' in filename:
        return True
    
    # Starts with dot = usually config file
    if filename.startswith('.'):
        return True
    
    return False

