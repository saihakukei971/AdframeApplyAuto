import datetime
import os

created_frames_save_folder = f"./created_frames/retry_records/{datetime.datetime.now().strftime('%Y%m%d')}"

def add_created_frames(frames : list, type: str):
    save_str = ",".join(frames)

    if not os.path.exists("./created_frames/retry_records"):
        os.mkdir("./created_frames/retry_records")
    if not os.path.exists(created_frames_save_folder):
        os.mkdir(created_frames_save_folder)
    with open(f"{created_frames_save_folder}/{type}.txt", mode='a', encoding="UTF-8") as f:
        f.write(save_str + "\n")

def check_created_frames(frames : list, type: str) -> bool:
    saved_str = ",".join(frames)
    try:
        with open(f"{created_frames_save_folder}/{type}.txt", mode='r', encoding="UTF-8") as f:
            for line in f:
                if (line == saved_str + "\n"):
                    return True
    except FileNotFoundError:
        return False
    return False
