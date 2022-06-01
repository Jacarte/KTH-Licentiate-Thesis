import imageio
import os

with imageio.get_writer('movie.gif', mode='I', fps=35) as writer:
    frames = os.listdir("out")
    frames = [f for f in frames if f != ".DS_Store"]
    frames = sorted(frames, key=lambda x: int(x.replace("img", "").replace(".png", "")))
    frames = list(frames)
    #print(frames)
    for filename in frames:
        print(filename)
        try:
            image = imageio.imread(f"out/{filename}")
            writer.append_data(image)
        except Exception as e:
            break