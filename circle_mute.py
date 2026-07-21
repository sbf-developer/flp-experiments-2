from PIL import Image, ImageDraw, ImageFont

src = r"C:\Users\scott\.cursor\projects\c-Users-scott-Desktop-dev-flp\assets\c__Users_scott_AppData_Roaming_Cursor_User_workspaceStorage_a3ed6026831340952bb5dff479836a96_images_image-ebc3c7bd-82e0-4907-8dde-bd981c7a3b3c.png"
out = r"c:\Users\scott\Desktop\dev\flp\out\mute_tool_circled.png"

im = Image.open(src).convert("RGBA")
ann = im.copy()
d = ImageDraw.Draw(ann)

def circle(cx, cy, r, color=(255, 25, 25, 255)):
    for t in range(4):
        d.ellipse((cx - r - t, cy - r - t, cx + r + t, cy + r + t), outline=color)

def label(x, y, text, w=260):
    d.rectangle((x, y, x + w, y + 28), fill=(0, 0, 0, 235), outline=(255, 40, 40, 255), width=2)
    d.text((x + 8, y + 7), text, fill=(255, 90, 90, 255))

# Playlist toolbar mute = 4th icon in paint/draw/delete/mute group.
# For this 1024x625 capture, that cluster is under the playlist title,
# roughly starting near x=330 after the left pattern list.
# Icons ~20px: 1=paint~338, 2=draw~358, 3=delete~378, 4=MUTE~398
circle(398, 98, 24)
label(430, 28, "1) MUTE TOOL (speaker)", w=230)
d.line((398, 74, 450, 56), fill=(255, 30, 30, 255), width=3)

# Pencil is first icon — tell them to click that
circle(338, 98, 22, color=(40, 220, 80, 255))
for t in range(4):
    d.ellipse((338 - 22 - t, 98 - 22 - t, 338 + 22 + t, 98 + 22 + t), outline=(40, 220, 80, 255))
d.rectangle((40, 28, 300, 56), fill=(0, 0, 0, 235), outline=(40, 220, 80, 255), width=2)
d.text((50, 35), "2) click PENCIL to turn mute off", fill=(80, 255, 120, 255))
d.line((338, 76, 280, 56), fill=(40, 220, 80, 255), width=3)

ann.convert("RGB").save(out, quality=95)
print("saved", out)
