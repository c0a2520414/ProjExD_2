import os
import random
import sys
import pygame as pg
import time

WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#2行あける
def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect or 爆弾Rect
    戻り値：判定結果タプル（横方向判定結果、縦方向判定結果）
    True：画面内|False：画面外
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right: #横方向判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: #縦方向判定
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示する関数
    引数：screen（画面Surface)
    """

    bg_img = pg.image.load("fig/pg_bg.jpg")
    screen.blit(bg_img, [0, 0])

    black = pg.Surface((WIDTH, HEIGHT))
    black.fill((0, 0, 0)) # Surfaceを一色に塗りつぶす
    black.set_alpha(128) # 透明度

    screen.blit(black,[0, 0]) # 左上ぴったり([0, 0])の場所に貼り付ける

    font = pg.font.Font(None, 80) # フォント名、サイズ
    gmo = font.render("Game Over", True, (255, 255, 255)) # 白字で"Game Over"と書かれたSurfaceインスタンスを生成する
    gmo_rct = gmo.get_rect() # Game Overの画像から位置やサイズを監理するための見えない四角い枠を取得する
    gmo_rct.center = (WIDTH // 2, HEIGHT // 2)
    screen.blit(gmo, gmo_rct)

    kk_cry = pg.image.load("fig/8.png")

    kk_l_rct = kk_cry.get_rect()
    kk_l_rct.center = (WIDTH // 2 - 200, HEIGHT // 2)
    screen.blit(kk_cry, kk_l_rct)

    kk_r_rct = kk_cry.get_rect()
    kk_r_rct.center = (WIDTH // 2 + 200, HEIGHT // 2)
    screen.blit(kk_cry, kk_r_rct)

    pg.display.update() # 更新
    time.sleep(5) # 5秒間表示


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    サイズの違う爆弾Surfaceのリストと、加速度のリストを準備する関数
    戻り値：（爆弾Surfaceのリスト、加速度のリスト）のタプル
    """
    bb_imgs = []
    for r in range(1,11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        pg.draw.circle(bb_img, (255, 0, 0),(10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1,11)]

    return bb_imgs, bb_accs

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    #こうかとんの初期化
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    #爆弾の初期化
    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0] 
    bb_rct = bb_img.get_rect() # 爆弾rct
    bb_rct.centerx = random.randint(0, WIDTH) # 横初期座標
    bb_rct.centery = random.randint(0, HEIGHT) # 縦初期座標
    vx, vy = +5, +5

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct): # こうかとんRectと爆弾Rectが重なったら
            gameover(screen)
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        #if key_lst[pg.K_UP]:
        #    sum_mv[1] -= 5
        #if key_lst[pg.K_DOWN]:
        #    sum_mv[1] += 5
        #if key_lst[pg.K_LEFT]:
        #    sum_mv[0] -= 5
        #if key_lst[pg.K_RIGHT]:
        #    sum_mv[0] += 5

        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0] #横方向の移動量
                sum_mv[1] += mv[1] #縦方向の移動量
    
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1]) # 動きをなかったことにする
        screen.blit(kk_img, kk_rct)

        idx = min(tmr // 500, 9) # tmrが0~499のとき=0,500~999のとき=1,1000~1499のとき=2:最大値は9に固定
        avx = vx*bb_accs[idx]
        avy = vy*bb_accs[idx]
        bb_img = bb_imgs[idx]

        bb_center = bb_rct.center # 今の爆弾の中心座標を、一時的にメモしておく
        bb_rct = bb_img.get_rect() # 大きくなった新しい画像に合わせて、四角い枠を作り直す
        bb_rct.center = bb_center # 作り直した枠の中心を、さっきメモした元の中心位置に合わせる

        bb_rct.move_ip(avx, avy)

        yoko, tate = check_bound(bb_rct)
        if not yoko: # 横方向にはみ出ていたら
            vx *= -1
        if not tate: # 縦方向にはみ出ていたら
            vy *= -1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
