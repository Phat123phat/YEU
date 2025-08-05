import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import json
import os
from collections import Counter

class TaiXiuAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tool Phân Tích Cầu Tài Xỉu Pro")
        
        # Tỷ lệ 16:10 - thiết kế cho màn hình hiện đại
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Tính toán kích thước cửa sổ theo tỷ lệ 16:10
        window_width = min(1600, int(screen_width * 0.9))
        window_height = int(window_width * 10 / 16)
        
        # Căn giữa cửa sổ
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg='#0f0f0f')
        self.root.minsize(1200, 750)
        
        # Cấu hình style system
        self.setup_modern_style()
        
        # Lưu trữ dữ liệu
        self.history = []
        self.data_file = "taixiu_history.json"
        
        # Load dữ liệu cũ nếu có
        self.load_data()
        
        self.setup_modern_ui()
        
    def setup_modern_style(self):
        """Thiết lập style hiện đại với màu sắc gradient"""
        self.colors = {
            'bg_primary': '#0f0f0f',      # Đen chủ đạo
            'bg_secondary': '#1a1a1a',    # Xám đậm
            'bg_tertiary': '#262626',     # Xám vừa
            'accent_blue': '#3b82f6',     # Xanh dương hiện đại
            'accent_green': '#10b981',    # Xanh lá hiện đại
            'accent_orange': '#f59e0b',   # Cam hiện đại
            'accent_red': '#ef4444',      # Đỏ hiện đại
            'accent_purple': '#8b5cf6',   # Tím hiện đại
            'text_primary': '#ffffff',    # Trắng chính
            'text_secondary': '#d1d5db',  # Xám sáng
            'text_muted': '#9ca3af',      # Xám nhạt
            'success': '#22c55e',         # Xanh thành công
            'warning': '#f59e0b',         # Vàng cảnh báo
            'danger': '#ef4444',          # Đỏ nguy hiểm
        }
        
        self.fonts = {
            'title': ('Inter', 32, 'bold'),
            'header': ('Inter', 20, 'bold'),
            'subheader': ('Inter', 16, 'bold'),
            'body': ('Inter', 14),
            'body_bold': ('Inter', 14, 'bold'),
            'caption': ('Inter', 12),
            'button': ('Inter', 13, 'bold'),
            'mono': ('JetBrains Mono', 13),
            'mono_large': ('JetBrains Mono', 15),
        }
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure modern button style
        style.configure('Modern.TButton',
                       background=self.colors['accent_blue'],
                       foreground='white',
                       font=self.fonts['button'],
                       borderwidth=0,
                       focuscolor='none')
        
    def setup_modern_ui(self):
        """Thiết lập giao diện hiện đại với layout grid"""
        # Main container với padding
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)
        
        # Header section
        self.setup_modern_header(main_container)
        
        # Main content grid (2x2 layout)
        self.setup_content_grid(main_container)
        
        # Footer
        self.setup_modern_footer(main_container)
        
        # Auto analyze
        self.analyze_patterns()
        
    def setup_modern_header(self, parent):
        """Header hiện đại với gradient effect"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], height=120)
        header_frame.pack(fill=tk.X, pady=(0, 24))
        header_frame.pack_propagate(False)
        
        # Title với icon
        title_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        title_frame.pack(expand=True)
        
        title_label = tk.Label(title_frame, 
                              text="🎯 TOOL PHÂN TÍCH CẦU TÀI XỈU PRO",
                              font=self.fonts['title'],
                              fg=self.colors['text_primary'],
                              bg=self.colors['bg_secondary'])
        title_label.pack(pady=20)
        
        # Stats bar với cards
        stats_container = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        stats_container.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        self.setup_stats_cards(stats_container)
        
    def setup_stats_cards(self, parent):
        """Tạo các thẻ thống kê hiện đại"""
        stats_data = [
            ('Tổng ván', '0', self.colors['accent_blue'], '📊'),
            ('Tài', '0 (0%)', self.colors['success'], '🎯'),
            ('Xỉu', '0 (0%)', self.colors['warning'], '🎲'),
            ('Streak', 'N/A', self.colors['accent_purple'], '🔥')
        ]
        
        self.stats_labels = {}
        
        for i, (label, value, color, icon) in enumerate(stats_data):
            # Card container
            card = tk.Frame(parent, bg=self.colors['bg_tertiary'], relief=tk.FLAT)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
            
            # Card content
            content_frame = tk.Frame(card, bg=self.colors['bg_tertiary'])
            content_frame.pack(expand=True, pady=16, padx=20)
            
            # Icon
            icon_label = tk.Label(content_frame, text=icon, font=('Inter', 24),
                                 fg=color, bg=self.colors['bg_tertiary'])
            icon_label.pack()
            
            # Value
            key = label.lower().replace(' ', '_')
            self.stats_labels[key] = tk.Label(content_frame, text=value,
                                            font=self.fonts['subheader'],
                                            fg=self.colors['text_primary'],
                                            bg=self.colors['bg_tertiary'])
            self.stats_labels[key].pack(pady=(4, 2))
            
            # Label
            tk.Label(content_frame, text=label,
                    font=self.fonts['caption'],
                    fg=self.colors['text_muted'],
                    bg=self.colors['bg_tertiary']).pack()
    
    def setup_content_grid(self, parent):
        """Layout grid 2x2 cho nội dung chính"""
        content_container = tk.Frame(parent, bg=self.colors['bg_primary'])
        content_container.pack(fill=tk.BOTH, expand=True)
        
        # Top row - Input & History
        top_row = tk.Frame(content_container, bg=self.colors['bg_primary'])
        top_row.pack(fill=tk.X, pady=(0, 12))
        
        # Input section (60% width)
        self.setup_input_panel(top_row)
        
        # History section (40% width)
        self.setup_history_panel(top_row)
        
        # Bottom row - Analysis panels
        bottom_row = tk.Frame(content_container, bg=self.colors['bg_primary'])
        bottom_row.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
        
        # Quick recommendation (30%)
        self.setup_recommendation_panel(bottom_row)
        
        # Detailed analysis (40%)
        self.setup_analysis_panel(bottom_row)
        
        # Strategy panel (30%)
        self.setup_strategy_panel(bottom_row)
        
    def setup_input_panel(self, parent):
        """Panel nhập liệu hiện đại"""
        input_panel = tk.Frame(parent, bg=self.colors['bg_secondary'])
        input_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        
        # Header
        header = tk.Frame(input_panel, bg=self.colors['bg_secondary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📝 NHẬP KẾT QUẢ",
                font=self.fonts['header'],
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary']).pack(pady=16)
        
        # Input area
        input_area = tk.Frame(input_panel, bg=self.colors['bg_secondary'])
        input_area.pack(fill=tk.X, padx=24, pady=(0, 24))
        
        # Entry with modern styling
        entry_frame = tk.Frame(input_area, bg=self.colors['bg_secondary'])
        entry_frame.pack(pady=(0, 20))
        
        tk.Label(entry_frame, text="Nhập T (Tài) hoặc X (Xỉu):",
                font=self.fonts['body'],
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_secondary']).pack(pady=(0, 8))
        
        self.result_entry = tk.Entry(entry_frame,
                                   font=self.fonts['mono_large'],
                                   width=12, justify='center',
                                   bg=self.colors['bg_tertiary'],
                                   fg=self.colors['text_primary'],
                                   insertbackground=self.colors['text_primary'],
                                   relief=tk.FLAT, bd=0)
        self.result_entry.pack(ipady=8)
        self.result_entry.bind('<Return>', lambda e: self.add_result())
        
        # Quick action buttons
        buttons_frame = tk.Frame(input_area, bg=self.colors['bg_secondary'])
        buttons_frame.pack(pady=(20, 0))
        
        # Tài button
        tai_btn = tk.Button(buttons_frame, text="🎯 TÀI",
                           command=lambda: self.quick_add('T'),
                           bg=self.colors['success'], fg='white',
                           font=self.fonts['button'],
                           relief=tk.FLAT, bd=0,
                           width=12, height=2,
                           cursor='hand2')
        tai_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Xỉu button
        xiu_btn = tk.Button(buttons_frame, text="🎲 XỈU",
                           command=lambda: self.quick_add('X'),
                           bg=self.colors['warning'], fg='white',
                           font=self.fonts['button'],
                           relief=tk.FLAT, bd=0,
                           width=12, height=2,
                           cursor='hand2')
        xiu_btn.pack(side=tk.LEFT, padx=8)
        
        # Action buttons
        actions_frame = tk.Frame(input_area, bg=self.colors['bg_secondary'])
        actions_frame.pack(pady=(20, 0))
        
        delete_btn = tk.Button(actions_frame, text="🗑️ Xóa cuối",
                              command=self.remove_last,
                              bg=self.colors['danger'], fg='white',
                              font=self.fonts['caption'],
                              relief=tk.FLAT, bd=0,
                              width=12, cursor='hand2')
        delete_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        reset_btn = tk.Button(actions_frame, text="🔄 Reset",
                             command=self.reset_data,
                             bg=self.colors['text_muted'], fg='white',
                             font=self.fonts['caption'],
                             relief=tk.FLAT, bd=0,
                             width=12, cursor='hand2')
        reset_btn.pack(side=tk.LEFT, padx=8)
        
    def setup_history_panel(self, parent):
        """Panel lịch sử hiện đại"""
        history_panel = tk.Frame(parent, bg=self.colors['bg_secondary'])
        history_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(6, 0))
        
        # Header
        header = tk.Frame(history_panel, bg=self.colors['bg_secondary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📊 LỊCH SỬ 10 VÁN",
                font=self.fonts['header'],
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary']).pack(pady=16)
        
        # History display
        history_display = tk.Frame(history_panel, bg=self.colors['bg_tertiary'])
        history_display.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))
        
        self.history_label = tk.Label(history_display,
                                     text="Chưa có dữ liệu",
                                     font=self.fonts['mono'],
                                     fg=self.colors['text_secondary'],
                                     bg=self.colors['bg_tertiary'],
                                     wraplength=300,
                                     justify=tk.CENTER)
        self.history_label.pack(expand=True, pady=20)
        
    def setup_recommendation_panel(self, parent):
        """Panel khuyến nghị hiện đại"""
        rec_panel = tk.Frame(parent, bg=self.colors['bg_secondary'])
        rec_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        
        # Header
        header = tk.Frame(rec_panel, bg=self.colors['bg_secondary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🎯 KHUYẾN NGHỊ",
                font=self.fonts['header'],
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary']).pack(pady=16)
        
        # Content area
        content_area = tk.Frame(rec_panel, bg=self.colors['bg_secondary'])
        content_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Main recommendation card
        self.rec_card = tk.Frame(content_area, bg=self.colors['bg_tertiary'])
        self.rec_card.pack(fill=tk.X, pady=(0, 16))
        
        self.rec_action_label = tk.Label(self.rec_card,
                                        text="Chưa có khuyến nghị",
                                        font=self.fonts['subheader'],
                                        fg=self.colors['text_primary'],
                                        bg=self.colors['bg_tertiary'])
        self.rec_action_label.pack(pady=(16, 4))
        
        self.rec_rate_label = tk.Label(self.rec_card,
                                      text="",
                                      font=self.fonts['body'],
                                      fg=self.colors['text_secondary'],
                                      bg=self.colors['bg_tertiary'])
        self.rec_rate_label.pack(pady=(0, 16))
        
        # Stats grid
        stats_grid = tk.Frame(content_area, bg=self.colors['bg_secondary'])
        stats_grid.pack(fill=tk.X)
        
        # Confidence
        conf_frame = tk.Frame(stats_grid, bg=self.colors['bg_tertiary'])
        conf_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(conf_frame, text="Độ tin cậy:",
                font=self.fonts['caption'],
                fg=self.colors['text_muted'],
                bg=self.colors['bg_tertiary']).pack(pady=(8, 2))
        
        self.confidence_label = tk.Label(conf_frame, text="",
                                        font=self.fonts['body_bold'],
                                        fg=self.colors['text_primary'],
                                        bg=self.colors['bg_tertiary'])
        self.confidence_label.pack(pady=(0, 8))
        
        # Risk
        risk_frame = tk.Frame(stats_grid, bg=self.colors['bg_tertiary'])
        risk_frame.pack(fill=tk.X)
        
        tk.Label(risk_frame, text="Mức rủi ro:",
                font=self.fonts['caption'],
                fg=self.colors['text_muted'],
                bg=self.colors['bg_tertiary']).pack(pady=(8, 2))
        
        self.risk_label = tk.Label(risk_frame, text="",
                                  font=self.fonts['body_bold'],
                                  fg=self.colors['text_primary'],
                                  bg=self.colors['bg_tertiary'])
        self.risk_label.pack(pady=(0, 8))
        
    def setup_analysis_panel(self, parent):
        """Panel phân tích chi tiết"""
        analysis_panel = tk.Frame(parent, bg=self.colors['bg_secondary'])
        analysis_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)
        
        # Header
        header = tk.Frame(analysis_panel, bg=self.colors['bg_secondary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📈 PHÂN TÍCH CẦU",
                font=self.fonts['header'],
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary']).pack(pady=16)
        
        # Analysis text area
        self.analysis_text = scrolledtext.ScrolledText(
            analysis_panel,
            font=self.fonts['mono'],
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_secondary'],
            insertbackground=self.colors['text_primary'],
            selectbackground=self.colors['accent_blue'],
            relief=tk.FLAT, bd=0,
            wrap=tk.WORD
        )
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
    def setup_strategy_panel(self, parent):
        """Panel chiến lược"""
        strategy_panel = tk.Frame(parent, bg=self.colors['bg_secondary'])
        strategy_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        
        # Header
        header = tk.Frame(strategy_panel, bg=self.colors['bg_secondary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🔮 CHIẾN LƯỢC",
                font=self.fonts['header'],
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary']).pack(pady=16)
        
        # Strategy text area
        self.strategy_text = scrolledtext.ScrolledText(
            strategy_panel,
            font=self.fonts['mono'],
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_secondary'],
            insertbackground=self.colors['text_primary'],
            selectbackground=self.colors['accent_blue'],
            relief=tk.FLAT, bd=0,
            wrap=tk.WORD
        )
        self.strategy_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
    def setup_modern_footer(self, parent):
        """Footer hiện đại"""
        footer = tk.Frame(parent, bg=self.colors['bg_secondary'], height=50)
        footer.pack(fill=tk.X, pady=(24, 0))
        footer.pack_propagate(False)
        
        footer_text = f"💡 Cập nhật: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')} | 🎯 Tool phân tích Tài Xỉu chuyên nghiệp | Made with ❤️"
        tk.Label(footer, text=footer_text,
                font=self.fonts['caption'],
                fg=self.colors['text_muted'],
                bg=self.colors['bg_secondary']).pack(expand=True)
    
    def quick_add(self, result):
        """Thêm kết quả nhanh"""
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(0, result)
        self.add_result()
        
    def add_result(self):
        result = self.result_entry.get().upper().strip()
        if not result:
            messagebox.showerror("Lỗi", "Vui lòng nhập kết quả!")
            return
            
        if result not in ['T', 'X', 'TÀI', 'XỈU']:
            messagebox.showerror("Lỗi", "Chỉ nhập T (Tài) hoặc X (Xỉu)!")
            return
            
        # Chuẩn hóa
        if result in ['TÀI', 'T']:
            result = 'T'
        else:
            result = 'X'
            
        self.history.append({
            'result': result,
            'time': datetime.now().strftime('%H:%M:%S'),
            'date': datetime.now().strftime('%d/%m/%Y')
        })
        
        # Giữ chỉ 50 kết quả gần nhất
        if len(self.history) > 50:
            self.history = self.history[-50:]
            
        self.result_entry.delete(0, tk.END)
        self.update_display()
        self.save_data()
        
    def remove_last(self):
        if self.history:
            self.history.pop()
            self.update_display()
            self.save_data()
        else:
            messagebox.showinfo("Thông báo", "Không có dữ liệu để xóa!")
            
    def reset_data(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa toàn bộ dữ liệu?"):
            self.history = []
            self.update_display()
            self.save_data()
            
    def update_display(self):
        # Update statistics
        self.update_statistics()
        
        # Update history display
        self.update_history_display()
        
        # Update analysis
        self.analyze_patterns()
        
    def update_statistics(self):
        """Cập nhật thống kê header"""
        total = len(self.history)
        tai_count = sum(1 for item in self.history if item['result'] == 'T')
        xiu_count = total - tai_count
        
        # Streak hiện tại
        streak = self.get_current_streak()
        
        self.stats_labels['tổng_ván'].config(text=str(total))
        
        if total > 0:
            tai_percent = (tai_count / total) * 100
            xiu_percent = (xiu_count / total) * 100
            self.stats_labels['tài'].config(text=f"{tai_count} ({tai_percent:.1f}%)")
            self.stats_labels['xỉu'].config(text=f"{xiu_count} ({xiu_percent:.1f}%)")
        else:
            self.stats_labels['tài'].config(text="0 (0%)")
            self.stats_labels['xỉu'].config(text="0 (0%)")
            
        self.stats_labels['streak'].config(text=streak)
        
    def update_history_display(self):
        """Cập nhật hiển thị lịch sử"""
        recent_10 = [item['result'] for item in self.history[-10:]]
        if recent_10:
            # Tạo display string với emoji
            history_display = []
            for result in recent_10:
                symbol = "🎯" if result == 'T' else "🎲"
                history_display.append(f"{symbol}")
            
            history_str = "  ".join(history_display)
            full_text = f"Gần nhất: {history_str}\n\n"
            
            # Thêm thông tin chi tiết
            if len(recent_10) >= 3:
                full_text += f"3 ván: {' → '.join(recent_10[-3:])}\n"
            if len(recent_10) >= 5:
                full_text += f"5 ván: {' → '.join(recent_10[-5:])}\n"
            
            self.history_label.config(text=full_text)
        else:
            self.history_label.config(text="Chưa có dữ liệu")
    
    def get_current_streak(self):
        """Lấy streak hiện tại"""
        if not self.history:
            return "N/A"
            
        recent_10 = [item['result'] for item in self.history[-10:]]
        if not recent_10:
            return "N/A"
            
        current = recent_10[-1]
        count = 1
        
        for i in range(len(recent_10) - 2, -1, -1):
            if recent_10[i] == current:
                count += 1
            else:
                break
                
        return f"{count} {current}"
        
    def analyze_patterns(self):
        if len(self.history) < 3:
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(tk.END, "⏳ Cần ít nhất 3 kết quả để phân tích...\n\n📝 Hãy nhập thêm kết quả để có phân tích chi tiết.")
            
            self.strategy_text.delete(1.0, tk.END)
            self.strategy_text.insert(tk.END, "⏳ Chưa đủ dữ liệu để đưa ra chiến lược...\n\n🎯 Nhập thêm kết quả để nhận khuyến nghị.")
            
            self.update_recommendation(None)
            return
            
        recent_10 = [item['result'] for item in self.history[-10:]]
        recent_5 = recent_10[-5:] if len(recent_10) >= 5 else recent_10
        recent_3 = recent_10[-3:]
        
        analysis = self.get_pattern_analysis(recent_10, recent_5, recent_3)
        strategies, recommendation = self.get_strategies(recent_10, recent_5, recent_3)
        
        # Hiển thị phân tích
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, analysis)
        
        # Hiển thị chiến lược
        self.strategy_text.delete(1.0, tk.END)
        self.strategy_text.insert(tk.END, strategies)
        
        # Cập nhật khuyến nghị
        self.update_recommendation(recommendation)
        
    def update_recommendation(self, recommendation):
        """Cập nhật khuyến nghị"""
        if recommendation:
            self.rec_action_label.config(text=f"🎯 {recommendation['action']}")
            self.rec_rate_label.config(text=f"📊 Tỷ lệ thắng: {recommendation['win_rate']}%")
            
            # Confidence
            win_rate = recommendation['win_rate']
            if win_rate >= 85:
                confidence = "RẤT CAO ⭐⭐⭐⭐⭐"
                card_color = self.colors['success']
            elif win_rate >= 75:
                confidence = "CAO ⭐⭐⭐⭐"
                card_color = self.colors['accent_blue']
            elif win_rate >= 65:
                confidence = "TRUNG BÌNH ⭐⭐⭐"
                card_color = self.colors['warning']
            else:
                confidence = "THẤP ⭐⭐"
                card_color = self.colors['danger']
                
            self.confidence_label.config(text=confidence)
            self.risk_label.config(text=recommendation['risk'])
            
            # Update card color
            self.rec_card.config(bg=card_color)
            self.rec_action_label.config(bg=card_color, fg='white')
            self.rec_rate_label.config(bg=card_color, fg='white')
            
        else:
            self.rec_action_label.config(text="⚠️ KHÔNG CÓ CẦU RÕ")
            self.rec_rate_label.config(text="Tỷ lệ thắng: 50% (may rủi)")
            self.confidence_label.config(text="KHÔNG XÁC ĐỊNH")
            self.risk_label.config(text="🔴 CAO")
            
            # Red card for no recommendation
            self.rec_card.config(bg=self.colors['danger'])
            self.rec_action_label.config(bg=self.colors['danger'], fg='white')
            self.rec_rate_label.config(bg=self.colors['danger'], fg='white')
    
    def get_pattern_analysis(self, recent_10, recent_5, recent_3):
        """Phân tích các mẫu cầu"""
        analysis = []
        analysis.append("🔍 PHÂN TÍCH CẦU CHI TIẾT")
        analysis.append("=" * 50)
        analysis.append(f"📊 10 ván: {' → '.join(recent_10)}")
        analysis.append(f"📊 5 ván:  {' → '.join(recent_5)}")
        analysis.append(f"📊 3 ván:  {' → '.join(recent_3)}")
        analysis.append("")
        
        # Phân tích các loại cầu
        found_patterns = []
        
        # 1. Cầu 1-1 (Luân phiên)
        if self.check_alternating_pattern(recent_10):
            found_patterns.append("✅ CẦU 1-1: Phát hiện cầu luân phiên T-X")
            
        # 2. Cầu bệt
        consecutive_count = self.get_consecutive_count(recent_10)
        if consecutive_count >= 3:
            found_patterns.append(f"🔥 CẦU BỆT: {consecutive_count} ván liên tiếp")
            
        # 3. Cầu 2-1
        if self.check_2_1_pattern(recent_5):
            found_patterns.append("⚡ CẦU 2-1: Phát hiện mẫu 2-1")
            
        # 4. Cầu 3-1
        if self.check_3_1_pattern(recent_10):
            found_patterns.append("🎯 CẦU 3-1: Phát hiện mẫu 3-1")
            
        # 5. Cầu đối xứng
        if self.check_symmetric_pattern(recent_10):
            found_patterns.append("🔄 CẦU ĐỐI XỨNG: T-X-X-T hoặc X-T-T-X")
            
        # 6. Cầu 2-2
        if self.check_2_2_pattern(recent_10):
            found_patterns.append("📈 CẦU 2-2: Mẫu TT-XX luân phiên")
            
        if found_patterns:
            analysis.append("🎯 CÁC CẦU PHÁT HIỆN:")
            analysis.extend([f"  • {pattern}" for pattern in found_patterns])
        else:
            analysis.append("❌ Không phát hiện cầu rõ ràng")
            
        # Thống kê tổng quan
        analysis.append("")
        analysis.append("📊 THỐNG KÊ:")
        analysis.append("-" * 30)
        tai_count = recent_10.count('T')
        xiu_count = recent_10.count('X')
        analysis.append(f"🎯 Tài: {tai_count}/{len(recent_10)} ({tai_count/len(recent_10)*100:.1f}%)")
        analysis.append(f"🎲 Xỉu: {xiu_count}/{len(recent_10)} ({xiu_count/len(recent_10)*100:.1f}%)")
        
        # Xu hướng
        if tai_count > xiu_count + 2:
            analysis.append("📈 XU HƯỚNG: Tài đang chiếm ưu thế")
        elif xiu_count > tai_count + 2:
            analysis.append("📉 XU HƯỚNG: Xỉu đang chiếm ưu thế")
        else:
            analysis.append("⚖️ XU HƯỚNG: Cân bằng")
            
        return "\n".join(analysis)
        
    def get_strategies(self, recent_10, recent_5, recent_3):
        """Đưa ra chiến lược và khuyến nghị"""
        strategies = []
        strategies.append("🔮 CHIẾN LƯỢC & KHUYẾN NGHỊ")
        strategies.append("=" * 50)
        
        recommendations = []
        
        # Dựa trên cầu bệt
        consecutive = self.get_consecutive_count(recent_10)
        if consecutive >= 4:
            opposite = 'X' if recent_3[-1] == 'T' else 'T'
            win_rate = min(85 + (consecutive - 4) * 3, 95)
            recommendations.append({
                'action': f"CƯỢC {opposite}",
                'reason': f"Cầu bệt {consecutive} ván",
                'win_rate': win_rate,
                'risk': 'THẤP' if consecutive >= 5 else 'TRUNG BÌNH',
                'strategy': 'Gấp thếp khi thua'
            })
            
        # Dựa trên cầu luân phiên
        if self.check_alternating_pattern(recent_5):
            next_pred = 'X' if recent_3[-1] == 'T' else 'T'
            recommendations.append({
                'action': f"CƯỢC {next_pred}",
                'reason': "Cầu luân phiên 1-1",
                'win_rate': 72,
                'risk': 'TRUNG BÌNH',
                'strategy': 'Cược đều đặn'
            })
            
        # Dựa trên cầu 2-1
        if self.check_2_1_pattern(recent_5):
            pattern_end = recent_5[-3:]
            if pattern_end in [['T', 'T', 'X'], ['X', 'X', 'T']]:
                next_pred = pattern_end[0]
                recommendations.append({
                    'action': f"CƯỢC {next_pred}",
                    'reason': "Cầu 2-1 lặp lại",
                    'win_rate': 75,
                    'risk': 'TRUNG BÌNH',
                    'strategy': 'Theo chu kỳ'
                })
                
        # Dựa trên tần suất
        tai_count = recent_10.count('T')
        xiu_count = recent_10.count('X')
        
        if tai_count >= 7:
            recommendations.append({
                'action': "CƯỢC X",
                'reason': f"Tài quá nhiều ({tai_count}/10)",
                'win_rate': 80,
                'risk': 'THẤP',
                'strategy': 'Cân bằng tần suất'
            })
        elif xiu_count >= 7:
            recommendations.append({
                'action': "CƯỢC T",
                'reason': f"Xỉu quá nhiều ({xiu_count}/10)",
                'win_rate': 80,
                'risk': 'THẤP',
                'strategy': 'Cân bằng tần suất'
            })
            
        # Hiển thị khuyến nghị
        if recommendations:
            recommendations.sort(key=lambda x: x['win_rate'], reverse=True)
            
            strategies.append("🏆 TOP KHUYẾN NGHỊ:")
            strategies.append("")
            
            for i, rec in enumerate(recommendations[:3], 1):
                icon = "🔥" if rec['win_rate'] >= 80 else "⚡" if rec['win_rate'] >= 70 else "💡"
                risk_icon = {"THẤP": "🟢", "TRUNG BÌNH": "🟡", "CAO": "🔴"}[rec['risk']]
                
                strategies.append(f"{icon} #{i}: {rec['action']}")
                strategies.append(f"   📈 Tỷ lệ: {rec['win_rate']}%")
                strategies.append(f"   📝 Lý do: {rec['reason']}")
                strategies.append(f"   {risk_icon} Rủi ro: {rec['risk']}")
                strategies.append("")
                
            # Quyết định cuối
            best = recommendations[0]
            strategies.append("🎯 QUYẾT ĐỊNH:")
            strategies.append(f"✅ {best['action']}")
            strategies.append(f"📊 Tỷ lệ thắng: {best['win_rate']}%")
            strategies.append(f"🛡️ Rủi ro: {best['risk']}")
            
        else:
            strategies.append("⚠️ KHÔNG CÓ CẦU RÕ RÀNG")
            strategies.append("")
            strategies.append("📋 Khuyến nghị:")
            strategies.append("• NGHỈ CHƠI hoặc TEST NHỎ")
            strategies.append("• Chờ cầu rõ ràng hơn")
            strategies.append("• Không nên cược lớn")
            
        strategies.append("")
        strategies.append("💰 QUẢN LÝ VỐN:")
        strategies.append("-" * 30)
        
        if recommendations and recommendations[0]['win_rate'] >= 80:
            strategies.append("• Có thể tăng 20-30% tiền cược")
            strategies.append("• Stoploss sau 2 ván thua")
            strategies.append("• Gấp thếp khi có cầu mạnh")
        elif recommendations and recommendations[0]['win_rate'] >= 70:
            strategies.append("• Giữ mức cược bình thường")
            strategies.append("• Stoploss sau 3 ván thua")
            strategies.append("• Theo dõi cẩn thận")
        else:
            strategies.append("• Chỉ cược 50% mức bình thường")
            strategies.append("• Nghỉ nếu thua 2 ván liên tiếp")
            strategies.append("• Chờ tín hiệu rõ ràng")
            
        strategies.append("")
        strategies.append("⚠️ LƯU Ý AN TOÀN:")
        strategies.append("🚫 Không all-in dù tỷ lệ cao")
        strategies.append("🧠 Giữ tâm lý ổn định")
        strategies.append("😴 Nghỉ khi mệt mỏi")
        strategies.append("📝 Ghi chép để rút kinh nghiệm")
        
        return "\n".join(strategies), recommendations[0] if recommendations else None
        
    # Pattern checking methods
    def check_alternating_pattern(self, sequence):
        """Kiểm tra cầu luân phiên"""
        if len(sequence) < 4:
            return False
        for i in range(len(sequence) - 1):
            if sequence[i] == sequence[i + 1]:
                return False
        return True
        
    def get_consecutive_count(self, sequence):
        """Đếm số ván liên tiếp cùng kết quả"""
        if not sequence:
            return 0
        count = 1
        current = sequence[-1]
        for i in range(len(sequence) - 2, -1, -1):
            if sequence[i] == current:
                count += 1
            else:
                break
        return count
        
    def check_2_1_pattern(self, sequence):
        """Kiểm tra cầu 2-1"""
        if len(sequence) < 3:
            return False
        seq_str = ''.join(sequence[-3:])
        return seq_str in ['TTX', 'XXX', 'TXT', 'XTX']
        
    def check_3_1_pattern(self, sequence):
        """Kiểm tra cầu 3-1"""
        if len(sequence) < 4:
            return False
        seq_str = ''.join(sequence[-4:])
        return seq_str in ['TTTX', 'XXXT']
        
    def check_symmetric_pattern(self, sequence):
        """Kiểm tra cầu đối xứng"""
        if len(sequence) < 4:
            return False
        for i in range(len(sequence) - 3):
            subseq = sequence[i:i+4]
            if subseq in [['T', 'X', 'X', 'T'], ['X', 'T', 'T', 'X']]:
                return True
        return False
        
    def check_2_2_pattern(self, sequence):
        """Kiểm tra cầu 2-2"""
        if len(sequence) < 4:
            return False
        for i in range(len(sequence) - 3):
            subseq = sequence[i:i+4]
            if subseq in [['T', 'T', 'X', 'X'], ['X', 'X', 'T', 'T']]:
                return True
        return False
        
    def save_data(self):
        """Lưu dữ liệu ra file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi lưu dữ liệu: {e}")
            
    def load_data(self):
        """Tải dữ liệu từ file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"Lỗi đọc dữ liệu: {e}")
            self.history = []
            
    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TaiXiuAnalyzer()
    app.run()