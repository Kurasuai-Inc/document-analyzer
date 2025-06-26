#!/usr/bin/env python3
"""
D3.js用のインタラクティブツリー生成ツール
Markdownファイルをウェブベースのインタラクティブツリーとして可視化
"""
import json
from pathlib import Path
from typing import Dict, List, Any
import webbrowser
import os


class D3TreeGenerator:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.md_files = []
        
    def scan_md_files(self) -> None:
        """mdファイルをスキャン"""
        for md_file in self.root_path.rglob("*.md"):
            # node_modules, .venv などを除外
            if any(excluded in md_file.parts for excluded in ["node_modules", ".venv", "__pycache__"]):
                continue
            
            relative_path = md_file.relative_to(self.root_path)
            self.md_files.append(relative_path)
        
        # ディレクトリ階層でソート
        self.md_files.sort()
    
    def build_tree_data(self) -> Dict[str, Any]:
        """D3.js用のツリーデータ構造を構築"""
        # シンプルな階層構造を構築
        def create_node(name, is_directory=False):
            return {
                "name": name,
                "type": "directory" if is_directory else "file",
                "children": [] if is_directory else None
            }
        
        # ルートノード作成
        root = create_node(f"{self.root_path.name}/", True)
        
        # ファイルをツリーに追加
        for md_file in self.md_files:
            parts = list(md_file.parts)
            current_node = root
            
            # パスを辿りながらディレクトリを作成
            for i, part in enumerate(parts):
                is_file = (i == len(parts) - 1)  # 最後の部分はファイル
                
                # 既存の子ノードを検索
                found_child = None
                for child in current_node["children"]:
                    if child["name"] == (part if is_file else f"{part}/"):
                        found_child = child
                        break
                
                # 子ノードが見つからない場合は新規作成
                if found_child is None:
                    new_node = create_node(part if is_file else f"{part}/", not is_file)
                    current_node["children"].append(new_node)
                    current_node = new_node
                else:
                    current_node = found_child
        
        return root
    
    def generate_html(self, output_path: str = "d3_tree.html") -> str:
        """インタラクティブHTML生成"""
        tree_data = self.build_tree_data()
        
        # HTMLテンプレート読み込み
        template_path = Path(__file__).parent / "d3_tree_visualizer.html"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # ツリーデータを埋め込み
            tree_json = json.dumps(tree_data, indent=4, ensure_ascii=False)
            
            # JavaScriptのサンプルデータを実際のデータに置換
            html_content = html_content.replace(
                '// Sample tree data (would be generated from Python backend)',
                '// Tree data generated from Python backend'
            )
            
            # サンプルデータを実際のデータに置換
            sample_start = html_content.find('const treeData = {')
            sample_end = html_content.find('};', sample_start) + 2
            
            if sample_start != -1 and sample_end != -1:
                before = html_content[:sample_start]
                after = html_content[sample_end:]
                html_content = before + f"const treeData = {tree_json};" + after
            
            # タイトルも更新
            stats_info = f"{len(self.md_files)} md files found"
            html_content = html_content.replace(
                "📁 Markdown Files D3 Tree Visualizer 🌳",
                f"📁 Markdown Files D3 Tree Visualizer 🌳<br><small>({stats_info})</small>"
            )
            
            # ファイル保存
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return output_path
            
        except FileNotFoundError:
            print(f"テンプレートファイルが見つかりません: {template_path}")
            return None
    
    def visualize(self, output_path: str = "d3_tree.html", open_browser: bool = True) -> str:
        """D3.jsインタラクティブツリーを生成"""
        self.scan_md_files()
        
        print(f"Found {len(self.md_files)} markdown files")
        
        # HTML生成
        html_path = self.generate_html(output_path)
        
        if html_path and open_browser:
            # ブラウザで開く
            full_path = Path(html_path).resolve()
            webbrowser.open(f"file://{full_path}")
            print(f"Interactive tree opened in browser: {html_path}")
        elif html_path:
            print(f"Interactive tree generated: {html_path}")
        
        return html_path


def main():
    """メイン実行関数"""
    # デフォルトはこのプロジェクトのルート（3階層上）
    root_path = Path(__file__).resolve().parent.parent.parent
    
    generator = D3TreeGenerator(root_path)
    html_path = generator.visualize()
    
    if html_path:
        print("D3.js Interactive Tree Visualization completed!")
        print(f"Open {html_path} in your browser to view the interactive tree")


if __name__ == '__main__':
    main()