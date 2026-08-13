"""Assembles hierarchical file and directory trees representing workspace structures.
"""

import os
from pathlib import Path
from typing import Dict, List
from app.agents.software_engineer.repository.models import FileInfo, RepositoryNode, RepositoryTree


def build_repository_tree(root_path: str, files: List[FileInfo]) -> RepositoryTree:
    """Builds a hierarchical RepositoryTree from flat list of FileInfos.

    Args:
        root_path: Absolute workspace root path.
        files: Flat list of scanned file details.

    Returns:
        Built RepositoryTree model.
    """
    abs_root = os.path.abspath(root_path)

    # Initialize root node
    root_node = RepositoryNode(
        absolute_path=abs_root,
        relative_path="",
        depth=0,
        node_type="directory",
        size=0,
        last_modified=os.path.getmtime(abs_root) if os.path.exists(abs_root) else 0.0,
    )

    nodes_map: Dict[str, RepositoryNode] = {"": root_node}

    # Extract all directories that contain these files
    all_rel_paths = set()
    for f in files:
        all_rel_paths.add(f.relative_path)
        # Traverse directories up to root
        parent_dir = os.path.dirname(f.relative_path)
        while parent_dir:
            all_rel_paths.add(parent_dir)
            parent_dir = os.path.dirname(parent_dir)

    # Sort relative paths by depth (number of segments) so we process parent directories first
    sorted_rel_paths = sorted(all_rel_paths, key=lambda p: len(Path(p).parts))

    for rel_path in sorted_rel_paths:
        abs_path = os.path.join(abs_root, rel_path)
        parts = Path(rel_path).parts
        depth = len(parts)
        parent_rel = os.path.dirname(rel_path)

        parent_node = nodes_map.get(parent_rel)
        if not parent_node:
            continue  # Safety check

        # Find matching FileInfo
        matching_file = next((f for f in files if f.relative_path == rel_path), None)

        if matching_file:
            # It's a file
            node = RepositoryNode(
                absolute_path=abs_path,
                relative_path=rel_path,
                depth=depth,
                node_type="file",
                size=matching_file.size,
                last_modified=matching_file.last_modified,
                language=matching_file.language,
                framework=matching_file.framework,
                parent=parent_node,
            )
            parent_node.children.append(node)
        else:
            # It's a directory
            # Size of directory is sum of sizes of files inside it
            dir_size = sum(
                f.size
                for f in files
                if f.relative_path.startswith(rel_path + "/")
                or f.relative_path == rel_path
            )
            node = RepositoryNode(
                absolute_path=abs_path,
                relative_path=rel_path,
                depth=depth,
                node_type="directory",
                size=dir_size,
                last_modified=os.path.getmtime(abs_path) if os.path.exists(abs_path) else 0.0,
                parent=parent_node,
            )
            parent_node.children.append(node)
            nodes_map[rel_path] = node

    # Compute root size
    root_node.size = sum(f.size for f in files)

    return RepositoryTree(root=root_node)
