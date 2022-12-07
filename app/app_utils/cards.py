import math

from PIL import Image, ImageDraw, ImageFont, ImageOps

FONT_PATH = "assets/GothamMedium.ttf"
ICON_PATH = "images/mfp-icon.png"
CARD_HEIGHT = 667
CARD_WIDTH = 375


def create_base_card(
    color,
    font_path=FONT_PATH,
    icon_path=ICON_PATH,
    height=CARD_HEIGHT,
    width=CARD_WIDTH,
):
    # create base card
    im = Image.new(mode="RGB", size=(width, height), color=color)
    draw = ImageDraw.Draw(im)

    # add mfp wrapped icon and text
    icon_fnt = ImageFont.truetype(font_path, 16)
    icon = Image.open(icon_path)
    icon = icon.resize((30, 30))
    im.paste(icon, (5, 5), icon)
    draw.text((40, 20), "mfp wrapped", font=icon_fnt, fill=(0, 0, 0))

    # add wrapped website
    draw.text(
        (width - 190, height - 20),
        "wrapped.ismailmo.com",
        font=icon_fnt,
        fill=(0, 0, 0),
    )
    return (draw, im)


def generate_total_kcal_card(num_kcal: int):
    draw, card = create_base_card((148, 240, 180))
    card_width, card_height = card.size
    font_size = 90
    title_fnt = ImageFont.truetype(FONT_PATH, font_size)
    _, _, num_kcal_w, _ = draw.textbbox(
        (0, 0), f"{num_kcal:,}", font=title_fnt
    )

    # shirnk font size for large total_kcal displays
    while num_kcal_w > card_width - 20:
        font_size -= 3
        title_fnt = ImageFont.truetype(FONT_PATH, font_size)
        _, _, num_kcal_w, _ = draw.textbbox(
            (0, 0), f"{num_kcal:,}", font=title_fnt
        )

    draw.text(
        (5, (card_height / 2) - 180),
        f"{num_kcal:,}",
        font=title_fnt,
        fill=(0, 0, 0),
    )

    # compare with household power consumption
    kcal_fnt = ImageFont.truetype(FONT_PATH, 20)
    fnt = ImageFont.truetype(FONT_PATH, 36)
    #  https://shrinkthatfootprint.com/average-household-electricity-consumption/
    # average household usage = 29kwH = 25000 kcal
    household_daily_usage_kcal = 25_000
    num_homes = num_kcal / household_daily_usage_kcal
    draw.text(
        (200, (card_height / 2) - 100),
        "Total calories",
        font=kcal_fnt,
        fill=(110, 110, 110),
    )

    draw.text(
        (20, (card_height / 2) - 75),
        f"Enough to power " f"\n{num_homes:.2f} average UK\nhomes for a day",
        font=fnt,
    )

    # add home icons
    home_img = Image.open("../app/images/home.png")
    home_imgs_top = 380
    num_cols = 4
    num_rows = math.ceil(num_homes / num_cols)
    home_img_width = 80
    w_pad = 3
    total_width = (home_img_width + w_pad) * num_cols
    total_height = (home_img_width * num_rows) + home_imgs_top
    home_img.thumbnail((home_img_width, home_img_width))

    avail_height = card_height - home_imgs_top - 50
    avail_width = card_width - 20

    height_clash = total_height > avail_height
    width_clash = total_width > avail_width

    while height_clash or width_clash:
        if height_clash:
            # increasing cols wont help for width clash
            num_cols += 1

        max_width_per_home = avail_width / num_cols
        home_img_width = int(max_width_per_home - w_pad)
        num_rows = math.ceil(num_homes / num_cols)
        total_width = (home_img_width + w_pad) * num_cols
        total_height = home_img_width * num_rows
        home_img.thumbnail((home_img_width, home_img_width))
        height_clash = total_height > avail_height
        width_clash = total_width > avail_width

    home_imgs = [home_img for _ in range(math.ceil(num_homes))]
    fraction = num_homes % 1
    if fraction > 0:
        card_width = home_img.size[0]
        home_imgs[-1] = home_img.crop((0, 0, int(card_width * fraction), 100))

    for idx, home in enumerate(home_imgs):
        row = idx // num_cols
        col = idx % num_cols
        card.paste(
            home,
            (
                20 + (home_img_width * col),
                (row * (w_pad + home_img_width)) + home_imgs_top,
            ),
            home,
        )

    return card


def generate_top_foods_card(top_entries: dict[str, int]):

    draw, top5_card = create_base_card((250, 250, 250))

    head_fnt = ImageFont.truetype(FONT_PATH, 30)
    num_fnt = ImageFont.truetype(FONT_PATH, 42)
    food_fnt = ImageFont.truetype(FONT_PATH, 30)
    qty_fnt = ImageFont.truetype(FONT_PATH, 18)

    draw.text(
        (12, 60), "Your top 5 food entries", fill=(0, 102, 238), font=head_fnt
    )

    for rank, (food, qty) in enumerate(top_entries.items()):
        rank += 1
        if len(food) > 18:
            food = food[:15] + "..."
        draw.text(
            (20, (rank * 100) + 30),
            f"#{rank}",
            fill=(150, 150, 150),
            font=num_fnt,
        )
        draw.text((90, (rank * 100) + 25), food, fill=(0, 0, 0), font=food_fnt)
        draw.text(
            (90, (rank * 100) + 55),
            f"{qty} entries",
            fill=(0, 84, 143),
            font=qty_fnt,
        )

    return top5_card


def generate_days_tracked_card(
    tracked_days, total_days, longest_streak, longest_blank
):
    draw, days_tracked_card = create_base_card((184, 89, 192))

    perc_days = tracked_days / total_days

    perc_font = ImageFont.truetype(FONT_PATH, 140)
    draw.text(
        (0, 120), f"{perc_days*100:.0f}%", font=perc_font, fill=(0, 0, 0, 200)
    )

    font = ImageFont.truetype(FONT_PATH, 40)
    draw.text(
        (10, 220),
        f"You entered food\n\tin your diary on\n\t\t{tracked_days} days\n\t\t"
        f"\tout of {total_days} ",
        font=font,
    )

    streak_font = ImageFont.truetype(FONT_PATH, 20)
    draw.text((30, 420), "Longest Streak", font=streak_font, fill=(0, 0, 0))
    draw.text((30, 445), f"{longest_streak} days", font=streak_font)

    draw.text((30, 500), "Longest Blank", font=streak_font, fill=(0, 0, 0))
    draw.text((30, 525), f"{longest_blank} days", font=streak_font)

    return days_tracked_card


def generate_adherence_card(adherence: float, tolerance: float = 0.1):
    draw, adherence_card = create_base_card((0, 102, 238))
    card_w, card_h = adherence_card.size

    phrase_imgs = (
        ("None of my business though", "../app/images/kermit.jpg"),
        (
            "Sometimes Maybe Good,\nSometimes Maybe Shit",
            "../app/images/gattuso.png",
        ),
        ("Mr Consistent", "../app/images/checklist.jpg"),
    )

    def get_adherence_level(adherence_perc: float):
        if adherence_perc < 0.3:
            return 0
        if adherence_perc > 0.7:
            return 2
        return 1

    threshold_lvl = get_adherence_level(adherence)
    phrase_font = ImageFont.truetype(FONT_PATH, 18)

    meme_img = Image.open(phrase_imgs[threshold_lvl][1])
    meme_img.thumbnail((180, 180))
    meme_img_border = ImageOps.expand(meme_img, border=5, fill=(0, 0, 0))
    meme_w, meme_h = meme_img_border.size
    img_top = 90
    adherence_card.paste(
        meme_img_border, (int((card_w - meme_w) / 2), img_top)
    )

    phrase = phrase_imgs[threshold_lvl][0]
    _, _, w, _ = draw.textbbox((0, 0), phrase, font=phrase_font)
    draw.text(
        ((card_w - w) / 2, img_top + meme_h + 10),
        phrase,
        font=phrase_font,
        align="center",
    )

    adherence_font = ImageFont.truetype(FONT_PATH, 42)
    draw.text(
        (20, 350),
        f"You met your\nnutrition goals\n{adherence*100:.0f}% of the time*",
        font=adherence_font,
    )

    disclaimer_font = ImageFont.truetype(FONT_PATH, 15)
    draw.text(
        (20, 550),
        f"*within {tolerance*100:.0f}% of kcal goal",
        font=disclaimer_font,
    )

    return adherence_card
