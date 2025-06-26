#!/usr/bin/env python3
"""
シンプルな静的ツリー画像生成ツール（色分け対応）
"""
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Tuple


class SimpleTreeVisualizer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.md_files = []
        
    def scan_md_files(self) -> None:
        """mdファイルをスキャン"""
        for md_file in self.root_path.rglob("*.md"):
            if any(excluded in md_file.parts for excluded in ["node_modules", ".venv", "__pycache__"]):
                continue
            
            relative_path = md_file.relative_to(self.root_path)
            self.md_files.append(relative_path)
        
        self.md_files.sort()
    
    def generate_tree_structure(self) -> List[Tuple[str, int, str]]:
        """ツリー構造を生成（行, インデント, タイプ）"""
        lines = []
        
        # ルートディレクトリ
        lines.append((f"{self.root_path.name}/ ({len(self.md_files)} md files)", 0, "root"))
        
        # ディレクトリ構造を構築
        dirs_processed = set()
        
        for md_file in self.md_files:
            parts = md_file.parts
            
            # ディレクトリ構造を表示
            for i, part in enumerate(parts[:-1]):
                dir_path = "/".join(parts[:i+1])
                if dir_path not in dirs_processed:
                    indent = i + 1
                    lines.append((f"|-- {part}/", indent, "directory"))
                    dirs_processed.add(dir_path)
            
            # ファイル名を表示
            indent = len(parts)
            filename = parts[-1]
            lines.append((f"+-- {filename}", indent, "file"))
        
        return lines
    
    def create_tree_image(self, output_path: str = "simple_tree.png") -> str:
        """色分け対応の静的ツリー画像を生成"""
        lines = self.generate_tree_structure()
        
        # 図のサイズを計算
        max_line_length = max(len(line[0]) + line[1] * 2 for line in lines)
        fig_width = max(16, max_line_length * 0.08)
        fig_height = max(12, len(lines) * 0.25)
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # 背景を白に設定
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        
        # フォント設定
        plt.rcParams['font.family'] = ['DejaVu Sans Mono', 'monospace']
        
        # 色の定義
        colors = {
            "root": "#2c3e50",        # 濃い青
            "directory": "#3498db",    # 青
            "file": "#27ae60"          # 緑
        }
        
        weights = {
            "root": "bold",
            "directory": "bold", 
            "file": "normal"
        }
        
        # ツリーテキストを描画
        y_pos = len(lines) - 1
        for line_text, indent, line_type in lines:
            # インデントを適用
            display_text = "  " * indent + line_text
            
            color = colors.get(line_type, "#000000")
            weight = weights.get(line_type, "normal")
            
            ax.text(0.02, y_pos, display_text, fontsize=11,
                   fontfamily='monospace', color=color, weight=weight,
                   verticalalignment='center')
            y_pos -= 1
        
        # 軸とフレームを非表示
        ax.set_xlim(0, 1)
        ax.set_ylim(-1, len(lines))
        ax.axis('off')
        
        # タイトルと凡例
        title = f"Markdown Files Tree Structure\\n{len(self.md_files)} files found"
        plt.title(title, fontsize=16, fontweight='bold', pad=30)
        
        # 凡例を追加
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors["directory"], 
                      markersize=8, label='📁 Directory'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors["file"], 
                      markersize=8, label='📄 Markdown File')
        ]
        
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
        
        # レイアウト調整
        plt.tight_layout()
        
        # 画像を保存
        plt.savefig(output_path, dpi=200, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return output_path
    
    def visualize(self, output_path: str = "simple_tree.png") -> str:
        """静的ツリーを生成"""
        self.scan_md_files()
        image_path = self.create_tree_image(output_path)
        return image_path


def main():
    """メイン実行関数"""
    root_path = Path(__file__).resolve().parent.parent.parent
    
    visualizer = SimpleTreeVisualizer(root_path)
    image_path = visualizer.visualize()
    
    print(f"Simple tree image generated: {image_path}")


if __name__ == '__main__':
    main()