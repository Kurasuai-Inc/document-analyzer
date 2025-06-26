#!/usr/bin/env python3
"""
ドキュメント分析ツール
Markdownドキュメント間のリンク関係を分析して、孤立したドキュメントを見つける
"""
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.tree import Tree


class DocumentAnalyzer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.documents: Dict[str, Path] = {}
        self.links: Dict[str, Set[str]] = {}
        self.incoming_links: Dict[str, Set[str]] = {}
        self.broken_links: Dict[str, List[Tuple[str, str]]] = {}  # doc_path -> [(link_text, link_url)]
        self.document_hashes: Dict[str, str] = {}
        self.duplicates: Dict[str, List[str]] = {}
        
    def scan_documents(self) -> None:
        """ドキュメントをスキャン"""
        for md_file in self.root_path.rglob("*.md"):
            # tools/node_modules/.venvディレクトリは除外
            if "node_modules" in md_file.parts or ".venv" in md_file.parts:
                continue
            relative_path = md_file.relative_to(self.root_path)
            self.documents[str(relative_path)] = md_file
            self.links[str(relative_path)] = set()
            self.incoming_links[str(relative_path)] = set()
            self.broken_links[str(relative_path)] = []
    
    def calculate_document_hashes(self) -> None:
        """各ドキュメントのハッシュ値を計算して重複を検出"""
        hash_to_docs: Dict[str, List[str]] = {}
        
        for doc_path, doc_file in self.documents.items():
            try:
                content = doc_file.read_text(encoding='utf-8')
                # 改行やスペースを正規化してからハッシュ値を計算
                normalized_content = '\n'.join(line.strip() for line in content.splitlines() if line.strip())
                file_hash = hashlib.md5(normalized_content.encode()).hexdigest()
                
                self.document_hashes[doc_path] = file_hash
                
                if file_hash in hash_to_docs:
                    hash_to_docs[file_hash].append(doc_path)
                else:
                    hash_to_docs[file_hash] = [doc_path]
            except Exception:
                pass
        
        # 重複を見つける
        self.duplicates = {hash_val: docs for hash_val, docs in hash_to_docs.items() if len(docs) > 1}
    
    def extract_links(self) -> None:
        """各ドキュメントからリンクを抽出"""
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        for doc_path, doc_file in self.documents.items():
            try:
                content = doc_file.read_text(encoding='utf-8')
                matches = link_pattern.findall(content)
                
                for link_text, link in matches:
                    # 外部リンクは除外
                    if link.startswith('http://') or link.startswith('https://'):
                        continue
                    
                    # アンカーリンクは除外
                    if link.startswith('#'):
                        continue
                    
                    # 相対パスを解決
                    if link.endswith('.md'):
                        target_path = self._resolve_link(doc_file, link)
                        if target_path:
                            self.links[doc_path].add(target_path)
                            self.incoming_links[target_path].add(doc_path)
                        else:
                            # リンク切れを記録
                            self.broken_links[doc_path].append((link_text, link))
            except Exception as e:
                print(f"Error reading {doc_path}: {e}")
    
    def _resolve_link(self, source_file: Path, link: str) -> str:
        """相対リンクを解決"""
        try:
            # ソースファイルのディレクトリを基準に解決
            source_dir = source_file.parent
            target_path = (source_dir / link).resolve().relative_to(self.root_path)
            
            # 実際に存在するか確認
            if str(target_path) in self.documents:
                return str(target_path)
        except Exception:
            pass
        return None
    
    def find_isolated_documents(self) -> List[str]:
        """孤立したドキュメントを見つける"""
        isolated = []
        for doc_path in self.documents:
            # CLAUDE.mdとREADME.mdは特別扱い（ルートドキュメント）
            if doc_path in ['CLAUDE.md', 'README.md']:
                continue
            
            # 入ってくるリンクがなく、出ていくリンクもない
            if not self.incoming_links.get(doc_path) and not self.links.get(doc_path):
                isolated.append(doc_path)
        
        return sorted(isolated)
    
    def get_statistics(self) -> Dict[str, int]:
        """統計情報を取得"""
        total_links = sum(len(links) for links in self.links.values())
        total_broken = sum(len(broken) for broken in self.broken_links.values())
        
        # 重複ファイルの総数を計算
        duplicate_count = sum(len(docs) - 1 for docs in self.duplicates.values())
        
        return {
            'total_documents': len(self.documents),
            'total_links': total_links,
            'isolated_documents': len(self.find_isolated_documents()),
            'documents_with_no_incoming': len([d for d in self.documents if not self.incoming_links.get(d)]),
            'documents_with_no_outgoing': len([d for d in self.documents if not self.links.get(d)]),
            'broken_links': total_broken,
            'duplicate_documents': duplicate_count
        }
    
    def build_tree_structure(self) -> Dict:
        """ディレクトリ構造からツリーを構築"""
        tree = {}
        
        for doc_path in self.documents:
            path = Path(doc_path)
            parts = path.parts
            
            current = tree
            # ディレクトリ階層を辿る
            for part in parts[:-1]:  # ファイル名以外
                if part not in current:
                    current[part] = {'type': 'dir', 'children': {}}
                current = current[part]['children']
            
            # ファイルを追加
            filename = parts[-1]
            current[filename] = {
                'type': 'file',
                'path': doc_path,
                'isolated': doc_path in self.find_isolated_documents()
            }
        
        return tree
    
    def generate_plantuml_mindmap(self, output_path: str = "document_mindmap.puml") -> str:
        """PlantUMLマインドマップ形式でツリーを生成
        
        Args:
            output_path: 出力ファイルのパス
            
        Returns:
            保存したファイルのパス
        """
        tree = self.build_tree_structure()
        
        plantuml_lines = [
            "@startmindmap",
            "* Document Root",
        ]
        
        def traverse(node_dict, depth=1):
            indent = "*" * (depth + 1)
            
            for name, info in node_dict.items():
                display_name = name.replace('.md', '').replace('-', '_')
                
                if info['type'] == 'dir':
                    # ディレクトリ
                    plantuml_lines.append(f"{indent} {display_name}")
                    traverse(info['children'], depth + 1)
                else:
                    # ファイル
                    plantuml_lines.append(f"{indent} {display_name}")
        
        traverse(tree)
        
        plantuml_lines.append("@endmindmap")
        
        # ファイルに保存
        output_file = Path(output_path)
        output_file.write_text('\n'.join(plantuml_lines), encoding='utf-8')
        
        return str(output_file)


def display_results(analyzer: DocumentAnalyzer, console: Console):
    """結果を表示"""
    # 統計情報
    stats = analyzer.get_statistics()
    
    # 統計テーブル
    stats_table = Table(title="ドキュメント統計", show_header=True, header_style="bold magenta")
    stats_table.add_column("項目", style="cyan")
    stats_table.add_column("数", justify="right", style="green")
    
    stats_table.add_row("総ドキュメント数", str(stats['total_documents']))
    stats_table.add_row("総リンク数", str(stats['total_links']))
    stats_table.add_row("孤立したドキュメント", str(stats['isolated_documents']))
    stats_table.add_row("入力リンクなし", str(stats['documents_with_no_incoming']))
    stats_table.add_row("出力リンクなし", str(stats['documents_with_no_outgoing']))
    stats_table.add_row("壊れたリンク", str(stats['broken_links']))
    stats_table.add_row("重複ドキュメント", str(stats['duplicate_documents']))
    
    console.print(stats_table)
    console.print()
    
    # 孤立したドキュメント
    isolated = analyzer.find_isolated_documents()
    if isolated:
        console.print("[bold red]孤立したドキュメント:[/bold red]")
        for doc in isolated:
            console.print(f"  • {doc}")
        console.print()
    
    # 壊れたリンク
    has_broken_links = False
    for doc_path, broken_links in analyzer.broken_links.items():
        if broken_links:
            has_broken_links = True
            break
    
    if has_broken_links:
        console.print("[bold red]壊れたリンク:[/bold red]")
        for doc_path, broken_links in sorted(analyzer.broken_links.items()):
            if broken_links:
                console.print(f"  [cyan]{doc_path}[/cyan]")
                for link_text, link_url in broken_links:
                    console.print(f"    • [{link_text}] → {link_url}")
        console.print()
    
    # 重複ドキュメント
    if analyzer.duplicates:
        console.print("[bold yellow]重複ドキュメント:[/bold yellow]")
        for hash_val, docs in analyzer.duplicates.items():
            console.print(f"  以下のファイルは内容が同一です:")
            for doc in sorted(docs):
                console.print(f"    • {doc}")
        console.print()
    
    # ドキュメントごとのリンク情報
    docs_table = Table(title="ドキュメント別リンク情報", show_header=True, header_style="bold blue")
    docs_table.add_column("ドキュメント", style="cyan")
    docs_table.add_column("出力リンク", justify="right", style="yellow")
    docs_table.add_column("入力リンク", justify="right", style="green")
    
    for doc_path in sorted(analyzer.documents.keys()):
        out_count = len(analyzer.links.get(doc_path, set()))
        in_count = len(analyzer.incoming_links.get(doc_path, set()))
        docs_table.add_row(doc_path, str(out_count), str(in_count))
    
    console.print(docs_table)


@click.command()
@click.option('--path', '-p', default=None, help='分析するルートパス')
@click.option('--verbose', '-v', is_flag=True, help='詳細情報を表示')
@click.option('--graph', '-g', is_flag=True, help='グラフを生成して表示')
@click.option('--mindmap', '-m', is_flag=True, help='PlantUMLマインドマップを生成')
@click.option('--discord', '-d', type=str, help='グラフをDiscordチャンネルに送信 (チャンネルID)')
def analyze(path: str, verbose: bool, graph: bool, mindmap: bool, discord: Optional[str]):
    """ドキュメントのリンク関係を分析"""
    console = Console()
    
    if path is None:
        # デフォルトはこのプロジェクトのルート（3階層上）
        root_path = Path(__file__).resolve().parent.parent.parent
    else:
        root_path = Path(path).resolve()
    console.print(f"[bold green]分析対象:[/bold green] {root_path}")
    console.print()
    
    analyzer = DocumentAnalyzer(root_path)
    
    # ドキュメントをスキャン
    analyzer.scan_documents()
    console.print(f"[cyan]{len(analyzer.documents)}個のドキュメントを発見[/cyan]")
    
    # リンクを抽出
    analyzer.extract_links()
    
    # ハッシュ値を計算して重複を検出
    analyzer.calculate_document_hashes()
    
    # 結果を表示
    display_results(analyzer, console)
    
    if verbose:
        # 詳細なリンク情報
        console.print("\n[bold yellow]詳細なリンク情報:[/bold yellow]")
        for doc_path, links in analyzer.links.items():
            if links:
                console.print(f"\n{doc_path}:")
                for link in sorted(links):
                    console.print(f"  → {link}")
    
    # マインドマップ生成
    if mindmap:
        try:
            mindmap_path = analyzer.generate_plantuml_mindmap()
            console.print(f"\n[bold green]PlantUMLマインドマップを生成しました:[/bold green] {mindmap_path}")
            
            # PlantUMLで画像生成を試す
            import subprocess
            try:
                result = subprocess.run(['plantuml', mindmap_path], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    png_path = mindmap_path.replace('.puml', '.png')
                    console.print(f"[bold green]PNG画像も生成しました:[/bold green] {png_path}")
                else:
                    console.print(f"[yellow]PlantUML実行エラー:[/yellow] {result.stderr}")
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                console.print(f"[yellow]PlantUMLコマンドが見つかりません。PUMLファイルのみ生成しました[/yellow]")
        except Exception as e:
            console.print(f"\n[bold red]エラー:[/bold red] マインドマップ生成中にエラーが発生しました: {str(e)}")
    
    # グラフ生成
    if graph or discord:
        try:
            from graph_visualizer import GraphVisualizer
            visualizer = GraphVisualizer(analyzer)
            
            # グラフを生成
            graph_path = visualizer.visualize()
            console.print(f"\n[bold green]グラフを生成しました:[/bold green] {graph_path}")
            
            # Discordに送信
            if discord:
                import os
                import sys
                # MCPツールを使うためのセットアップ
                console.print(f"\n[bold blue]Discordチャンネル {discord} に送信中...[/bold blue]")
                # 注: 実際のDiscord送信はMCPツール経由で行う必要がある
                console.print(f"[yellow]Discord送信機能は別途実装が必要です[/yellow]")
            
        except ImportError as e:
            console.print(f"\n[bold red]エラー:[/bold red] グラフ生成に必要なモジュールがありません: {str(e)}")
            console.print(f"以下のコマンドでインストールしてください:")
            console.print(f"uv add networkx matplotlib numpy")
        except Exception as e:
            console.print(f"\n[bold red]エラー:[/bold red] グラフ生成中にエラーが発生しました: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    analyze()