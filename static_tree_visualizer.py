#!/usr/bin/env python3
"""
静的ツリー画像生成ツール（色分け対応）
フォルダ・孤立ファイル・連結ファイルを色分けして表示
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re


class StaticTreeVisualizer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.md_files = []
        self.links = {}  # ファイル間のリンク関係
        self.incoming_links = {}
        
    def scan_md_files(self) -> None:
        """mdファイルをスキャンしてリンク関係も分析"""
        for md_file in self.root_path.rglob("*.md"):
            if any(excluded in md_file.parts for excluded in ["node_modules", ".venv", "__pycache__"]):
                continue
            
            relative_path = md_file.relative_to(self.root_path)
            self.md_files.append(relative_path)
            self.links[str(relative_path)] = set()
            self.incoming_links[str(relative_path)] = set()
        
        # リンク関係を分析
        self._extract_links()
        self.md_files.sort()
    
    def _extract_links(self) -> None:
        """ファイル間のリンク関係を抽出"""
        link_pattern = re.compile(r'\\[([^\\]]+)\\]\\(([^)]+)\\)')
        
        for md_file in self.md_files:
            file_path = self.root_path / md_file
            try:
                content = file_path.read_text(encoding='utf-8')
                matches = link_pattern.findall(content)
                
                for link_text, link_url in matches:
                    # 相対パスの解決
                    if link_url.startswith('./') or not link_url.startswith(('http', 'mailto', '#')):
                        target_path = self._resolve_link_path(md_file, link_url)
                        if target_path and target_path in [str(f) for f in self.md_files]:
                            self.links[str(md_file)].add(target_path)
                            self.incoming_links[target_path].add(str(md_file))
            except Exception:
                pass
    
    def _resolve_link_path(self, from_file: Path, link_url: str) -> str:
        """リンクパスを解決"""
        if link_url.startswith('./'):
            link_url = link_url[2:]
        
        # 現在のファイルのディレクトリを基準に解決
        current_dir = from_file.parent
        target_path = (current_dir / link_url).resolve()
        
        try:
            relative_target = target_path.relative_to(self.root_path)
            return str(relative_target)
        except ValueError:
            return None
    
    def classify_files(self) -> Tuple[Set[str], Set[str], Set[str]]:
        """ファイルを分類（孤立・連結・通常）"""
        isolated_files = set()
        connected_files = set()
        normal_files = set()
        
        for file_path in [str(f) for f in self.md_files]:
            has_outgoing = len(self.links.get(file_path, set())) > 0
            has_incoming = len(self.incoming_links.get(file_path, set())) > 0
            
            if not has_outgoing and not has_incoming:
                isolated_files.add(file_path)
            elif has_outgoing or has_incoming:
                connected_files.add(file_path)
            else:
                normal_files.add(file_path)
        
        return isolated_files, connected_files, normal_files
    
    def generate_tree_structure(self) -> List[Tuple[str, int, str, str]]:
        """ツリー構造を生成（行, インデント, タイプ, パス）"""
        isolated, connected, normal = self.classify_files()
        lines = []
        
        # ルートディレクトリ
        lines.append((f"{self.root_path.name}/ ({len(self.md_files)} md files)", 0, "root", ""))
        
        # ディレクトリ構造を構築
        dirs_processed = set()
        
        for md_file in self.md_files:
            parts = md_file.parts
            file_str = str(md_file)
            
            # ディレクトリ構造を表示
            for i, part in enumerate(parts[:-1]):
                dir_path = "/".join(parts[:i+1])
                if dir_path not in dirs_processed:
                    indent = i + 1
                    lines.append((f"|-- {part}/", indent, "directory", dir_path))
                    dirs_processed.add(dir_path)
            
            # ファイル分類
            if file_str in isolated:
                file_type = "isolated"
            elif file_str in connected:
                file_type = "connected"
            else:
                file_type = "normal"
            
            # ファイル名を表示
            indent = len(parts)
            filename = parts[-1]
            lines.append((f"+-- {filename}", indent, file_type, file_str))
        
        return lines
    
    def create_tree_image(self, output_path: str = "static_tree.png") -> str:
        """色分け対応の静的ツリー画像を生成"""
        lines = self.generate_tree_structure()
        
        # 図のサイズを計算
        max_line_length = max(len(line[0]) + line[1] * 2 for line in lines)
        fig_width = max(16, max_line_length * 0.08)
        fig_height = max(12, len(lines) * 0.3)
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # 背景を白に設定
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        
        # フォント設定（日本語対応）
        try:
            plt.rcParams['font.family'] = ['DejaVu Sans Mono', 'monospace']
        except:
            plt.rcParams['font.family'] = ['monospace']
        
        # 色の定義
        colors = {
            "root": "#2c3e50",        # 濃い青
            "directory": "#3498db",    # 青
            "connected": "#27ae60",    # 緑（リンクありファイル）
            "isolated": "#e74c3c",     # 赤（孤立ファイル）
            "normal": "#7f8c8d"        # グレー（通常ファイル）
        }
        
        weights = {
            "root": "bold",
            "directory": "bold",
            "connected": "normal",
            "isolated": "normal",
            "normal": "normal"
        }
        
        # ツリーテキストを描画
        y_pos = len(lines) - 1
        for line_text, indent, line_type, file_path in lines:
            # インデントを適用
            display_text = "  " * indent + line_text
            
            color = colors.get(line_type, "#000000")
            weight = weights.get(line_type, "normal")
            
            ax.text(0.02, y_pos, display_text, fontsize=10,
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
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors["connected"], 
                      markersize=8, label='🔗 Connected File'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors["isolated"], 
                      markersize=8, label='🔴 Isolated File'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors["normal"], 
                      markersize=8, label='📄 Normal File')
        ]
        
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
        
        # レイアウト調整
        plt.tight_layout()
        
        # 画像を保存
        plt.savefig(output_path, dpi=200, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return output_path
    
    def visualize(self, output_path: str = "static_tree.png") -> str:
        """静的ツリーを生成"""
        self.scan_md_files()
        image_path = self.create_tree_image(output_path)
        return image_path


def main():
    """メイン実行関数"""
    root_path = Path(__file__).resolve().parent.parent.parent
    
    visualizer = StaticTreeVisualizer(root_path)
    image_path = visualizer.visualize()
    
    print(f"Static tree image generated: {image_path}")
    
    # 統計情報
    isolated, connected, normal = visualizer.classify_files()
    print(f"\\nFile classification:")
    print(f"  Connected files: {len(connected)}")
    print(f"  Isolated files: {len(isolated)}")
    print(f"  Normal files: {len(normal)}")


if __name__ == '__main__':
    main()