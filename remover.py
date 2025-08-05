import numpy as np
import librosa
import soundfile as sf
import argparse
import os
from pathlib import Path

class VocalRemover:
    def __init__(self):
        """
        Khởi tạo Vocal Remover tool
        """
        self.supported_formats = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
    
    def remove_vocals_center_channel(self, audio_data, sample_rate):
        """
        Loại bỏ vocal bằng phương pháp center channel extraction
        
        Args:
            audio_data: numpy array chứa dữ liệu audio (stereo)
            sample_rate: tần số lấy mẫu
            
        Returns:
            numpy array: audio đã loại bỏ vocal
        """
        if len(audio_data.shape) == 1:
            print("⚠️  File audio là mono, không thể loại bỏ vocal")
            return audio_data
        
        if audio_data.shape[0] != 2:
            print("⚠️  File audio không phải stereo, chuyển đổi...")
            # Nếu có nhiều hơn 2 channel, chỉ lấy 2 channel đầu
            audio_data = audio_data[:2, :]
        
        # Lấy left và right channel
        left_channel = audio_data[0, :]
        right_channel = audio_data[1, :]
        
        # Loại bỏ vocal bằng cách trừ left - right
        # Vocal thường ở center (giống nhau ở cả 2 channel)
        vocal_removed = left_channel - right_channel
        
        return vocal_removed
    
    def remove_vocals_spectral(self, audio_data, sample_rate):
        """
        Loại bỏ vocal bằng phương pháp spectral subtraction (nâng cao hơn)
        
        Args:
            audio_data: numpy array chứa dữ liệu audio (stereo)
            sample_rate: tần số lấy mẫu
            
        Returns:
            numpy array: audio đã loại bỏ vocal
        """
        if len(audio_data.shape) == 1:
            return audio_data
        
        if audio_data.shape[0] != 2:
            audio_data = audio_data[:2, :]
        
        left_channel = audio_data[0, :]
        right_channel = audio_data[1, :]
        
        # Chuyển đổi sang domain tần số
        left_stft = librosa.stft(left_channel)
        right_stft = librosa.stft(right_channel)
        
        # Tính toán phase difference
        phase_diff = np.angle(left_stft) - np.angle(right_stft)
        
        # Loại bỏ những tần số có phase difference nhỏ (vocal thường có phase giống nhau)
        mask = np.abs(phase_diff) > 0.5  # Threshold có thể điều chỉnh
        
        # Áp dụng mask
        vocal_removed_stft = (left_stft - right_stft) * mask
        
        # Chuyển ngược về time domain
        vocal_removed = librosa.istft(vocal_removed_stft)
        
        return vocal_removed
    
    def enhance_audio(self, audio_data, sample_rate):
        """
        Cải thiện chất lượng audio sau khi loại bỏ vocal
        
        Args:
            audio_data: numpy array
            sample_rate: tần số lấy mẫu
            
        Returns:
            numpy array: audio đã được cải thiện
        """
        # Normalize audio
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Áp dụng high-pass filter để loại bỏ noise tần số thấp
        from scipy.signal import butter, filtfilt
        
        # Thiết kế high-pass filter
        nyquist = sample_rate / 2
        low_cutoff = 80  # Hz
        high_cutoff = low_cutoff / nyquist
        
        b, a = butter(4, high_cutoff, btype='high')
        filtered_audio = filtfilt(b, a, audio_data)
        
        return filtered_audio
    
    def process_file(self, input_path, output_path=None, method='center', enhance=True):
        """
        Xử lý file audio để loại bỏ vocal
        
        Args:
            input_path: đường dẫn file input
            output_path: đường dẫn file output (optional)
            method: phương pháp ('center' hoặc 'spectral')
            enhance: có cải thiện chất lượng audio không
        """
        input_path = Path(input_path)
        
        # Kiểm tra file tồn tại
        if not input_path.exists():
            raise FileNotFoundError(f"File không tồn tại: {input_path}")
        
        # Kiểm tra định dạng file
        if input_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Định dạng file không được hỗ trợ: {input_path.suffix}")
        
        print(f"🎵 Đang xử lý: {input_path.name}")
        
        # Đọc file audio
        try:
            audio_data, sample_rate = librosa.load(input_path, sr=None, mono=False)
            print(f"📊 Sample rate: {sample_rate} Hz")
            print(f"📊 Channels: {audio_data.shape[0] if len(audio_data.shape) > 1 else 1}")
            print(f"📊 Duration: {audio_data.shape[-1] / sample_rate:.2f} seconds")
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file audio: {e}")
        
        # Loại bỏ vocal
        if method == 'center':
            processed_audio = self.remove_vocals_center_channel(audio_data, sample_rate)
        elif method == 'spectral':
            processed_audio = self.remove_vocals_spectral(audio_data, sample_rate)
        else:
            raise ValueError("Method phải là 'center' hoặc 'spectral'")
        
        # Cải thiện chất lượng audio
        if enhance:
            print("✨ Đang cải thiện chất lượng audio...")
            processed_audio = self.enhance_audio(processed_audio, sample_rate)
        
        # Tạo tên file output
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_no_vocal{input_path.suffix}"
        else:
            output_path = Path(output_path)
        
        # Lưu file
        try:
            sf.write(output_path, processed_audio, sample_rate)
            print(f"✅ Đã lưu file: {output_path}")
            print(f"📁 Kích thước: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        except Exception as e:
            raise Exception(f"Lỗi khi lưu file: {e}")
        
        return str(output_path)
    
    def batch_process(self, input_folder, output_folder=None, method='center', enhance=True):
        """
        Xử lý hàng loạt file trong thư mục
        
        Args:
            input_folder: thư mục chứa file input
            output_folder: thư mục output (optional)
            method: phương pháp loại bỏ vocal
            enhance: có cải thiện chất lượng không
        """
        input_folder = Path(input_folder)
        
        if not input_folder.exists():
            raise FileNotFoundError(f"Thư mục không tồn tại: {input_folder}")
        
        # Tìm tất cả file audio
        audio_files = []
        for ext in self.supported_formats:
            audio_files.extend(input_folder.glob(f"*{ext}"))
            audio_files.extend(input_folder.glob(f"*{ext.upper()}"))
        
        if not audio_files:
            print("❌ Không tìm thấy file audio nào!")
            return
        
        print(f"🔍 Tìm thấy {len(audio_files)} file audio")
        
        # Tạo thư mục output
        if output_folder is None:
            output_folder = input_folder / "no_vocal"
        else:
            output_folder = Path(output_folder)
        
        output_folder.mkdir(exist_ok=True)
        
        # Xử lý từng file
        successful = 0
        failed = 0
        
        for i, audio_file in enumerate(audio_files, 1):
            try:
                print(f"\n[{i}/{len(audio_files)}] ", end="")
                output_path = output_folder / f"{audio_file.stem}_no_vocal{audio_file.suffix}"
                self.process_file(audio_file, output_path, method, enhance)
                successful += 1
            except Exception as e:
                print(f"❌ Lỗi xử lý {audio_file.name}: {e}")
                failed += 1
        
        print(f"\n📊 Kết quả: {successful} thành công, {failed} thất bại")

def simple_gui():
    """
    Giao diện đơn giản để chọn file
    """
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
        
        def select_input_file():
            file_path = filedialog.askopenfilename(
                title="Chọn file nhạc",
                filetypes=[
                    ("Audio files", "*.mp3 *.wav *.flac *.m4a *.ogg"),
                    ("MP3 files", "*.mp3"),
                    ("WAV files", "*.wav"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                input_var.set(file_path)
        
        def select_output_file():
            file_path = filedialog.asksaveasfilename(
                title="Chọn nơi lưu file",
                defaultextension=".wav",
                filetypes=[
                    ("WAV files", "*.wav"),
                    ("MP3 files", "*.mp3"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                output_var.set(file_path)
        
        def process_audio():
            input_path = input_var.get()
            if not input_path:
                messagebox.showerror("Lỗi", "Vui lòng chọn file input!")
                return
            
            output_path = output_var.get() if output_var.get() else None
            method = method_var.get()
            enhance = enhance_var.get()
            
            try:
                progress_bar.start()
                process_btn.config(state='disabled')
                root.update()
                
                remover = VocalRemover()
                result = remover.process_file(input_path, output_path, method, enhance)
                
                progress_bar.stop()
                process_btn.config(state='normal')
                
                messagebox.showinfo("Thành công", f"Đã xử lý xong!\nFile lưu tại: {result}")
                
            except Exception as e:
                progress_bar.stop()
                process_btn.config(state='normal')
                messagebox.showerror("Lỗi", str(e))
        
        # Tạo window
        root = tk.Tk()
        root.title("Vocal Remover Tool")
        root.geometry("600x400")
        
        # Variables
        input_var = tk.StringVar()
        output_var = tk.StringVar()
        method_var = tk.StringVar(value="center")
        enhance_var = tk.BooleanVar(value=True)
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input file
        ttk.Label(main_frame, text="File nhạc input:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=input_var, width=50).grid(row=1, column=0, pady=5)
        ttk.Button(main_frame, text="Chọn file", command=select_input_file).grid(row=1, column=1, padx=(5,0), pady=5)
        
        # Output file
        ttk.Label(main_frame, text="File output (để trống = tự động):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=output_var, width=50).grid(row=3, column=0, pady=5)
        ttk.Button(main_frame, text="Chọn nơi lưu", command=select_output_file).grid(row=3, column=1, padx=(5,0), pady=5)
        
        # Method
        ttk.Label(main_frame, text="Phương pháp:").grid(row=4, column=0, sticky=tk.W, pady=5)
        method_frame = ttk.Frame(main_frame)
        method_frame.grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(method_frame, text="Center Channel (nhanh)", variable=method_var, value="center").pack(side=tk.LEFT)
        ttk.Radiobutton(method_frame, text="Spectral (chất lượng cao)", variable=method_var, value="spectral").pack(side=tk.LEFT, padx=(20,0))
        
        # Enhance option
        ttk.Checkbutton(main_frame, text="Cải thiện chất lượng audio", variable=enhance_var).grid(row=6, column=0, sticky=tk.W, pady=10)
        
        # Process button
        process_btn = ttk.Button(main_frame, text="Bắt đầu xử lý", command=process_audio)
        process_btn.grid(row=7, column=0, pady=20)
        
        # Progress bar
        progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        progress_bar.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Instructions
        instructions = """
        Hướng dẫn sử dụng:
        1. Chọn file nhạc cần loại bỏ vocal
        2. Chọn nơi lưu file (hoặc để trống để tự động tạo tên)
        3. Chọn phương pháp xử lý
        4. Click "Bắt đầu xử lý"
        
        Lưu ý: Hiệu quả tốt nhất với nhạc stereo có vocal ở center
        """
        ttk.Label(main_frame, text=instructions, justify=tk.LEFT, foreground="gray").grid(row=9, column=0, columnspan=2, pady=20)
        
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        root.mainloop()
        
    except ImportError:
        print("❌ Không thể import tkinter. Vui lòng cài đặt tkinter hoặc sử dụng command line.")
        return False
    
    return True

def main():
    # Kiểm tra xem có arguments không
    import sys
    if len(sys.argv) == 1:
        # Không có arguments, chạy GUI
        print("🎵 Khởi động giao diện...")
        if not simple_gui():
            # Nếu GUI không chạy được, chạy demo
            demo_mode()
        return 0
    
    parser = argparse.ArgumentParser(description="Vocal Remover Tool - Loại bỏ giọng hát khỏi file nhạc")
    
    parser.add_argument("input", help="File audio hoặc thư mục input")
    parser.add_argument("-o", "--output", help="File hoặc thư mục output")
    parser.add_argument("-m", "--method", choices=['center', 'spectral'], 
                       default='center', help="Phương pháp loại bỏ vocal (default: center)")
    parser.add_argument("--no-enhance", action="store_true", 
                       help="Không cải thiện chất lượng audio")
    parser.add_argument("-b", "--batch", action="store_true", 
                       help="Xử lý hàng loạt file trong thư mục")
    
    args = parser.parse_args()
    
    # Khởi tạo vocal remover
    remover = VocalRemover()
    
    try:
        if args.batch or os.path.isdir(args.input):
            # Batch processing
            remover.batch_process(
                input_folder=args.input,
                output_folder=args.output,
                method=args.method,
                enhance=not args.no_enhance
            )
        else:
            # Single file processing
            output_file = remover.process_file(
                input_path=args.input,
                output_path=args.output,
                method=args.method,
                enhance=not args.no_enhance
            )
            print(f"\n🎉 Hoàn thành! File đã được lưu tại: {output_file}")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return 1
    
    return 0

def demo_mode():
    """
    Chế độ demo khi không có GUI
    """
    print("🎵 VOCAL REMOVER TOOL - DEMO MODE")
    print("=" * 50)
    
    # Hướng dẫn sử dụng
    print("Để sử dụng tool này, bạn có thể:")
    print("\n1. Sử dụng trong code Python:")
    print("""
from vocal_remover import VocalRemover

remover = VocalRemover()
output_file = remover.process_file("input_song.mp3", method='center', enhance=True)
    """)
    
    print("\n2. Sử dụng command line:")
    print("python remover.py input_song.mp3 -o output_song.wav")
    print("python remover.py /path/to/music/folder -b")
    
    print("\n3. Hardcode để test:")
    
    # Tìm file audio trong thư mục hiện tại để demo
    current_dir = Path(".")
    audio_files = []
    for ext in ['.mp3', '.wav', '.flac', '.m4a', '.ogg']:
        audio_files.extend(current_dir.glob(f"*{ext}"))
        audio_files.extend(current_dir.glob(f"*{ext.upper()}"))
    
    if audio_files:
        print(f"\n🔍 Tìm thấy {len(audio_files)} file audio trong thư mục hiện tại:")
        for i, file in enumerate(audio_files[:5], 1):  # Chỉ hiển thị 5 file đầu
            print(f"   {i}. {file.name}")
        
        choice = input(f"\nNhập số file muốn xử lý (1-{min(5, len(audio_files))}) hoặc Enter để bỏ qua: ")
        
        if choice.isdigit() and 1 <= int(choice) <= len(audio_files):
            selected_file = audio_files[int(choice) - 1]
            print(f"\n🎵 Đang xử lý: {selected_file.name}")
            
            try:
                remover = VocalRemover()
                output_file = remover.process_file(str(selected_file), method='center', enhance=True)
                print(f"\n🎉 Hoàn thành! File đã được lưu tại: {output_file}")
            except Exception as e:
                print(f"❌ Lỗi: {e}")
    else:
        print("\n❌ Không tìm thấy file audio nào trong thư mục hiện tại")
        print("Vui lòng copy file nhạc vào thư mục này và chạy lại")

if __name__ == "__main__":
    exit(main())