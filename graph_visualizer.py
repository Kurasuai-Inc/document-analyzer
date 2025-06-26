#!/usr/bin/env python3
"""
グラフ可視化モジュール
ドキュメント間のリンク関係をグラフとして可視化し、画像として保存する
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import networkx as nx
from pathlib import Path
from typing import Dict, Set, Optional
import numpy as np


class GraphVisualizer:
    def __init__(self, analyzer):
        """
        Args:
            analyzer: DocumentAnalyzerのインスタンス
        """
        self.analyzer = analyzer
        # 日本語フォントの設定
        self._setup_japanese_font()
    
    def _setup_japanese_font(self):
        """日本語フォントを設定"""
        import platform
        system = platform.system()
        
        # 優先順位の高い日本語フォントリスト
        font_candidates = []
        
        if system == 'Linux':
            font_candidates = [
                'Noto Sans CJK JP',
                'Noto Sans JP',
                'IPAexGothic',
                'IPAPGothic', 
                'TakaoGothic',
                'VL Gothic',
                'Droid Sans Japanese',
                'Ubuntu'
            ]
        elif system == 'Darwin':  # macOS
            font_candidates = [
                'Hiragino Sans',
                'Hiragino Kaku Gothic Pro',
                'Yu Gothic',
                'Osaka',
                'Meiryo'
            ]
        elif system == 'Windows':
            font_candidates = [
                'Yu Gothic',
                'Meiryo',
                'MS Gothic',
                'MS PGothic'
            ]
        
        # システムフォントから候補を探す
        found_font = None
        available_fonts = set([f.name for f in fm.fontManager.ttflist])
        
        for font_name in font_candidates:
            if font_name in available_fonts:
                found_font = font_name
                break
        
        # フォントパスから直接探す（fallback）
        if not found_font:
            font_paths = fm.findSystemFonts()
            for font_path in font_paths:
                font_lower = font_path.lower()
                if any(keyword in font_lower for keyword in ['noto', 'ipa', 'takao', 'gothic', 'sans']):
                    try:
                        prop = fm.FontProperties(fname=font_path)
                        found_font = prop.get_name()
                        break
                    except:
                        continue
        
        # フォントを設定
        if found_font:
            plt.rcParams['font.family'] = found_font
            plt.rcParams['font.sans-serif'] = [found_font]
            print(f"Using Japanese font: {found_font}")
        else:
            # フォールバック（英語フォント）
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
            print("Warning: Japanese font not found, using default font")
        
        # マイナス記号の表示設定
        plt.rcParams['axes.unicode_minus'] = False
    
    def create_graph(self) -> nx.DiGraph:
        """有向グラフを作成"""
        G = nx.DiGraph()
        
        # ノードを追加
        for doc in self.analyzer.documents:
            # ファイル名を短縮（最後の2階層のみ表示）
            parts = Path(doc).parts
            if len(parts) > 2:
                label = '/'.join(parts[-2:])
            else:
                label = doc
            
            # 孤立ノードの判定
            is_isolated = doc in self.analyzer.find_isolated_documents()
            G.add_node(doc, label=label, isolated=is_isolated)
        
        # エッジを追加
        for source, targets in self.analyzer.links.items():
            for target in targets:
                G.add_edge(source, target)
        
        return G
    
    def visualize(self, output_path: str = "document_graph.png", 
                  show_labels: bool = True,
                  node_size: int = 3000,
                  figure_size: tuple = (20, 16)) -> str:
        """グラフを可視化して画像として保存
        
        Args:
            output_path: 出力画像のパス
            show_labels: ラベルを表示するか
            node_size: ノードのサイズ
            figure_size: 図のサイズ (width, height)
            
        Returns:
            保存した画像のパス
        """
        G = self.create_graph()
        
        # レイアウトアルゴリズムを選択
        if len(G.nodes()) < 20:
            pos = nx.spring_layout(G, k=3, iterations=50)
        else:
            pos = nx.kamada_kawai_layout(G)
        
        plt.figure(figsize=figure_size)
        
        # ノードの色分け
        node_colors = []
        for node in G.nodes():
            if G.nodes[node].get('isolated', False):
                node_colors.append('#ff6b6b')  # 赤：孤立ノード
            elif G.in_degree(node) == 0:
                node_colors.append('#ffd43b')  # 黄：入力リンクなし
            elif G.out_degree(node) == 0:
                node_colors.append('#51cf66')  # 緑：出力リンクなし
            else:
                node_colors.append('#339af0')  # 青：通常ノード
        
        # ノードを描画
        nx.draw_networkx_nodes(G, pos, 
                              node_color=node_colors,
                              node_size=node_size,
                              alpha=0.9)
        
        # エッジを描画
        nx.draw_networkx_edges(G, pos,
                              edge_color='gray',
                              arrows=True,
                              arrowsize=20,
                              alpha=0.5,
                              connectionstyle="arc3,rad=0.1")
        
        # ラベルを描画
        if show_labels:
            labels = nx.get_node_attributes(G, 'label')
            nx.draw_networkx_labels(G, pos, labels,
                                   font_size=10,
                                   font_color='black',
                                   font_weight='bold')
        
        # 凡例を追加
        legend_elements = [
            plt.scatter([], [], c='#ff6b6b', s=100, label='孤立ノード'),
            plt.scatter([], [], c='#ffd43b', s=100, label='入力リンクなし'),
            plt.scatter([], [], c='#51cf66', s=100, label='出力リンクなし'),
            plt.scatter([], [], c='#339af0', s=100, label='通常ノード')
        ]
        plt.legend(handles=legend_elements, loc='upper right', fontsize=12)
        
        # タイトルと統計情報
        stats = self.analyzer.get_statistics()
        title = f"ドキュメントリンクグラフ\n"
        title += f"ノード数: {stats['total_documents']} | "
        title += f"リンク数: {stats['total_links']} | "
        title += f"孤立: {stats['isolated_documents']}"
        plt.title(title, fontsize=16, fontweight='bold')
        
        plt.axis('off')
        plt.tight_layout()
        
        # 画像を保存
        plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return output_path
    
    def create_minimap(self, output_path: str = "document_minimap.png") -> str:
        """簡略化されたミニマップを作成
        
        Args:
            output_path: 出力画像のパス
            
        Returns:
            保存した画像のパス
        """
        return self.visualize(
            output_path=output_path,
            show_labels=False,
            node_size=500,
            figure_size=(10, 8)
        )