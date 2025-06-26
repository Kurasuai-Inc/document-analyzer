#!/usr/bin/env python3
"""
Markdownファイル専用ツリー表示ツール
ディレクトリ構造に合わせてmdファイルのみをツリー構造で可視化
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
from typing import Dict, List, Tuple
import os


class MDTreeVisualizer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.md_files = []
        self.tree_structure = {}
        
    def scan_md_files(self) -> None:
        """mdファイルをスキャンしてツリー構造を構築"""
        for md_file in self.root_path.rglob("*.md"):
            # node_modules, .venv などを除外
            if any(excluded in md_file.parts for excluded in ["node_modules", ".venv", "__pycache__"]):
                continue
            
            relative_path = md_file.relative_to(self.root_path)
            self.md_files.append(relative_path)
        
        # ディレクトリ階層でソート
        self.md_files.sort()
        
    def build_tree_structure(self) -> Dict:
        """ツリー構造を辞書形式で構築"""
        tree = {}
        
        for md_file in self.md_files:
            parts = md_file.parts
            current = tree
            
            # ディレクトリ部分を処理
            for part in parts[:-1]:  # 最後のファイル名を除く
                if part not in current:
                    current[part] = {"__files__": [], "__dirs__": {}}
                current = current[part]["__dirs__"]
            
            # ファイル名を追加
            parent_dir = tree
            for part in parts[:-1]:
                parent_dir = parent_dir[part]["__dirs__"]
            
            if "__files__" not in parent_dir:
                parent_dir["__files__"] = []
            parent_dir["__files__"].append(parts[-1])
        
        # ルートレベルのファイル処理
        root_files = [f for f in self.md_files if len(f.parts) == 1]
        if root_files:
            tree["__files__"] = [f.name for f in root_files]
        
        return tree
    
    def generate_tree_text(self) -> str:
        """テキスト形式のツリーを生成"""
        tree = self.build_tree_structure()
        lines = []
        
        def add_tree_lines(node, prefix="", is_last=True):
            # ファイルを処理
            files = node.get("__files__", [])
            dirs = node.get("__dirs__", {})
            
            # ディレクトリを処理
            dir_items = list(dirs.items())
            for i, (dirname, subnode) in enumerate(dir_items):
                is_last_dir = (i == len(dir_items) - 1) and len(files) == 0
                connector = "└── " if is_last_dir else "├── "
                lines.append(f"{prefix}{connector}{dirname}/")
                
                extension = "    " if is_last_dir else "│   "
                add_tree_lines(subnode, prefix + extension, is_last_dir)
            
            # ファイルを処理
            for i, filename in enumerate(files):
                is_last_file = (i == len(files) - 1)
                connector = "└── " if is_last_file else "├── "
                lines.append(f"{prefix}{connector}{filename}")
        
        # ルートから開始
        lines.append(f"{self.root_path.name}/")
        add_tree_lines(tree)
        
        return "\n".join(lines)
    
    def create_tree_image(self, output_path: str = "md_tree.png") -> str:
        """ツリーを画像として生成"""
        tree_text = self.generate_tree_text()
        lines = tree_text.split('\n')
        
        # 図のサイズを計算
        max_line_length = max(len(line) for line in lines)
        fig_width = max(12, max_line_length * 0.1)
        fig_height = max(8, len(lines) * 0.3)
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # 背景を白に設定
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        
        # フォント設定
        plt.rcParams['font.family'] = ['DejaVu Sans Mono', 'monospace']
        
        # ツリーテキストを描画
        y_pos = len(lines) - 1
        for line in lines:
            # ディレクトリとファイルで色分け
            if line.strip().endswith('/'):
                color = 'blue'
                weight = 'bold'
            elif '.md' in line:
                color = 'darkgreen'
                weight = 'normal'
            else:
                color = 'black'
                weight = 'normal'
            
            ax.text(0.01, y_pos, line, fontsize=10, 
                   fontfamily='monospace', color=color, weight=weight,
                   verticalalignment='center')
            y_pos -= 1
        
        # 軸とフレームを非表示
        ax.set_xlim(0, 1)
        ax.set_ylim(-1, len(lines))
        ax.axis('off')
        
        # タイトル
        plt.title(f"Markdown Files Tree Structure\n{len(self.md_files)} files found", 
                 fontsize=14, fontweight='bold', pad=20)
        
        # レイアウト調整
        plt.tight_layout()
        
        # 画像を保存
        plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return output_path
    
    def visualize(self, output_path: str = "md_tree.png") -> Tuple[str, str]:
        """mdファイルのツリーを可視化"""
        self.scan_md_files()
        
        # テキスト版も生成
        tree_text = self.generate_tree_text()
        
        # 画像版を生成
        image_path = self.create_tree_image(output_path)
        
        return tree_text, image_path


def main():
    """メイン実行関数"""
    # デフォルトはこのプロジェクトのルート（3階層上）
    root_path = Path(__file__).resolve().parent.parent.parent
    
    visualizer = MDTreeVisualizer(root_path)
    tree_text, image_path = visualizer.visualize()
    
    print("Markdown Files Tree Structure:")
    print("=" * 50)
    print(tree_text)
    print("=" * 50)
    print(f"Image saved to: {image_path}")


if __name__ == '__main__':
    main()