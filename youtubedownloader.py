import tkinter as tk
from tkinter import ttk
from pytube import YouTube
import customtkinter
import os
import json
import re
import time  # time modülünü ekleyin

# İlerleme güncellemesi için kuyruk
progress_queue = []

def create_main_window():
    global root
    global progress
    global progressbar
    global url_var
    global output_path
    global download_hq
    global download_lq
    global download_audio  # download_hq, download_lq ve download_audio değişkenlerini global olarak tanımlayın

    root = customtkinter.CTk()
    root.title('Youtube Downloader by Ayhan')
    root.geometry("720x480")

    # Pencereyi yeniden boyutlandıramaz yap
    root.resizable(width=False, height=False)

    # Create a notebook (tabbed interface)
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # Create a frame for the main functionality
    main_frame = ttk.Frame(notebook)
    notebook.add(main_frame, text='Main')

    # Insert a Youtube Link
    title = customtkinter.CTkLabel(main_frame, text="Insert a Youtube Link", width=200, height=500,
                                   font=("cursive", 28))
    title.pack(padx=10, pady=10)

    global url_var
    url_var = tk.StringVar()  # url_var burada tanımlanıyor
    link = customtkinter.CTkEntry(main_frame, width=500, height=50, textvariable=url_var)
    link.pack(side="top", padx=10, pady=10)
    link.place(x=100, y=100)

    # Progress Percentage
    progress = customtkinter.CTkLabel(main_frame, text="0%")
    progress.place(x=345, y=160)

    # ProgressBar
    progressbar = customtkinter.CTkProgressBar(main_frame, width=400)
    progressbar.set(0)
    progressbar.place(x=155, y=200)


    # Download HQ Video
    download_hq = customtkinter.CTkButton(main_frame, text="Download HD Mp4",
                                          command=lambda: startDownload("highQuality"))
    download_hq.place(x=270, y=270)

    # Download LQ Video
    download_lq = customtkinter.CTkButton(main_frame, text="Download LQ Mp4",
                                          command=lambda: startDownload("lowQuality"))
    download_lq.place(x=270, y=310)

    # Download Audio Button
    download_audio = customtkinter.CTkButton(main_frame, text="Download Mp3", command=lambda: startDownload("audio"))
    download_audio.place(x=270, y=350)

    # Create a frame for the settings
    settings_frame = ttk.Frame(notebook)
    notebook.add(settings_frame, text='Settings')

    # İndirme yolu ayarları
    output_label = customtkinter.CTkLabel(settings_frame, text="İndirme Yolu:")
    output_label.grid(row=0, column=0)

    global output_path
    output_path = tk.StringVar()
    output_path_entry = customtkinter.CTkEntry(settings_frame, width=50, textvariable=output_path)
    output_path_entry.grid(row=0, column=1)

    # Load settings
    load_settings()

    # Altyazı seçeneği
    subtitle_var = tk.BooleanVar(value=False)
    subtitle_checkbox = ttk.Checkbutton(settings_frame, text="Altyazı indir", variable=subtitle_var)
    subtitle_checkbox.grid(row=1, column=0, columnspan=2, pady=5)

    # Ayarları kaydet ve yükle düğmeleri
    save_button = customtkinter.CTkButton(settings_frame, text="Ayarları Kaydet", command=save_settings)
    save_button.grid(row=1, column=0, columnspan=2)

    # Theme selection
    theme_frame = ttk.Frame(settings_frame)
    theme_frame.grid(row=2, column=0, columnspan=2, pady=10)

    theme_label = customtkinter.CTkLabel(theme_frame, text="Tema Seçimi:")
    theme_label.grid(row=0, column=0)

    theme_options = ["white", "green"]  # removed "black"
    theme_var = tk.StringVar(value="white")
    theme_menu = ttk.OptionMenu(theme_frame, theme_var, *theme_options, command=set_theme)
    theme_menu.grid(row=0, column=1)

    # Run the application
    root.mainloop()


def startDownload(option):
    try:
        ytLink = url_var.get()
        ytObject = YouTube(ytLink, on_progress_callback=on_progress)

        # Geçersiz karakterleri kaldır
        title = re.sub(r'[\\/*?:"<>|]', '', ytObject.title)

        if option == "highQuality":
            video = ytObject.streams.get_highest_resolution()
        elif option == "lowQuality":
            video = ytObject.streams.get_lowest_resolution()
        elif option == "audio":
            # Audio olarak indirme yerine mp3 olarak indirelim
            video = ytObject.streams.filter(only_audio=True).first()
            audio_file = video.download(output_path=output_path.get(), filename=title)
            mp3_file = os.path.splitext(audio_file)[0] + ".mp3"
            os.rename(audio_file, mp3_file)
            return

        download_path = os.path.join(output_path.get(), title + "." + video.subtype)
        video.download(output_path=download_path)

        if option != "audio":
            # İndirme tamamlandığında kuyruğa mesaj koy
            progress_queue.append("done")

    except Exception as e:
        print("Hata oluştu:", e)
        input("Devam etmek için bir tuşa basın...")
        progress_queue.append("error")  # Hata durumunda "error" string'ini kuyruğa ekle
        print(e)
    finally:
        if option != "audio":
            # İndirme butonlarını tekrar etkinleştir
            download_hq["state"] = "normal"
            download_lq["state"] = "normal"
            download_audio["state"] = "normal"

    _check_progress()  # İlerleme güncellemelerini başlatın

    if option != "audio":
        # İndirme işlemi başladıktan sonra mesaj göster
        # İndirme butonlarını etkisiz hale getir
        download_hq["state"] = "disabled"
        download_lq["state"] = "disabled"
        download_audio["state"] = "disabled"

def _check_progress():
    try:
        if progress_queue:
            new_progress = progress_queue.pop(0)
            if isinstance(new_progress, str):
                # Eğer gelen değer string ise, hata mesajını işle
                if new_progress == "error":
                    print("Hata: İndirme sırasında bir hata oluştu.")
                elif new_progress == "done":
                    print("İndirme tamamlandı!")
            else:
                print(f"Yeni Değer: {new_progress}")
                progress.configure(text=str(new_progress) + '%')
                progressbar.set(float(new_progress) / 100)

                # İndirme tamamlandıysa mesajı gösterin
                if new_progress == 100:
                    pass

    except Exception as e:
        print(f"Hata: {e}")

    root.after(100, _check_progress)

def on_progress(stream, chunk, bytes_remaining):
    try:
        total_size = stream.filesize
        bytes_download = total_size - bytes_remaining
        percentage_of_completion = (bytes_download / total_size) * 100
        progress_queue.append(int(percentage_of_completion))
    except Exception as e:
        print("İlerleme güncelleme hatası:", e)

def save_settings():
    download_path = output_path.get()
    settings = {"download_path": download_path}
    with open("settings.json", "w") as file:
        json.dump(settings, file)
    print("Ayarlar kaydedildi:")
    print("İndirme Yolu:", download_path)

def load_settings():
    try:
        with open("settings.json", "r") as file:
            settings = json.load(file)
            download_path = settings.get("download_path", "")
            output_path.set(download_path)
    except FileNotFoundError:
        output_path.set("")

def set_theme(theme):
    if theme == "white":
        customtkinter.set_default_color_theme("white")
    elif theme == "green":
        customtkinter.set_default_color_theme("green")

    # Arayüzü yeniden yükle
    root.destroy()
    create_main_window()

# Create the main window
create_main_window()
