import math
import random
import sys
import time

import pygame as pg
from pygame.sprite import AbstractGroup


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ


def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（爆弾，こうかとん，ビーム）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or HEIGHT < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"ex04/fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }

        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.state = "nomal" #コウカトンの初期状態をノーマルに設定
        self.hyper_life = -1 #無敵状態の時間を-1に初期設定する

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"ex04/fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)
    
    def change_state(self,state,hyper_life):
        """
        こうかとんの状態を切り替えるメゾット
        引数1 state: 状態を表す
        引数2 hyper_life: 発動時間
        """
        self.state = state
        self.hyper_life = hyper_life

    def change_state(self, state:str, hyper_life:int):
        """コウカトンの状態を切り替えるメソッド
        引数1 state:コウカトンの状態(normal or hyper)
        引数２ hyper:ハイパーモードの発動時間"""
        self.state = state
        self.hyper_life = hyper_life

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        if key_lst[pg.K_LSHIFT]:    #追加機能１　高速化
            self.speed = 20
        else:
            self.speed = 10

        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(self.rect) != (True, True):
            for k, mv in __class__.delta.items():
                if key_lst[k]:
                    self.rect.move_ip(-self.speed*mv[0], -self.speed*mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]


        if self.state == "hyper":#コウカトンがハイパー状態なら
            self.image = pg.transform.laplacian(self.image)#透明になる（画像変わる）
            self.hyper_life -= 1 #無敵モードの時間を1フレームごとに500から1引いていく
        if self.hyper_life < 0: #無敵モードに時間が0以下になったら
            self.change_state("nomal",-1) #ノーマルモードに戻す

        screen.blit(self.image, self.rect)
    
    def get_direction(self) -> tuple[int, int]:
        return self.dire
    def change_state(self,state:str,hyper_life:int):
        self.hyper_life = hyper_life
        self.state = state  # 追加機能2 #

        if self.state == "hyper":
            self.hyper_life -= 1
            self.image = pg.transform.laplacian(self.image)
            if self.hyper_life < 0:
                self.change_state("normal", -1)

        screen.blit(self.image, self.rect)

    def get_direction(self) -> tuple[int, int]:
        return self.dire
    

class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height/2
        self.speed = 6

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)

        if check_bound(self.rect) != (True, True):#爆弾が画面外にでたらグループから削除する

            self.kill()


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird, angle0=0):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        引数 angle0:neobeam時の角度
        """
        super().__init__()
        self.vx, self.vy = bird.get_direction()
        angle = math.degrees(math.atan2(-self.vy, self.vx)) + angle0
        self.image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/beam.png"), angle, 2.0)

        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10
        
        
    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()

class NeoBeam():
    """
    複数のビーム
    """
    def __init__(self, bird: Bird, num: int): 
        self.bird = bird
        self.num = num
        self.beams =list()
        
    def gen_beams(self):
        for angle in range(-50, 51, int(100/(self.num-1))):
            self.beams.append(Beam(self.bird, angle))
        return self.beams
            
            
        
        
        lst = []
        for i in range(self.num):
            Beam()
            lst.append(-50+(100/self.num*i))
        return lst
    
    
class NeoBeam:
    """
    複数ビームに関するクラス
    """
    def __init__(self, bird, num):
        """
        引数1:こうかとん
        引数2:ビーム数
        """
        self.bird = bird
        self.num = num
        
    def gen_beams(self):
        """
        ビームを生成する
        戻り値:ビームのリスト
        """
        lst = []
        for i in range(-50, +51, 100//(self.num-1)):
            beam = Beam(self.bird, i)
            lst.append(beam)
        return lst
    

class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load("ex04/fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()

class Shield(pg.sprite.Sprite):
    def __init__(self, bird:Bird, life:int):
        super().__init__()
        self.vx, self.vy = bird.get_direction()
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.image =pg.transform.rotozoom(pg.Surface((20, bird.rect.height * 2)),angle,1.0)
        pg.draw.rect(self.image,(0, 0, 0), pg.Rect(0,0,20, bird.rect.height*2))
        self.rect = self.image.get_rect()
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.life = life

    def update(self):
        self.life -= 1
        if self.life < 0:
            self.kill()



class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"ex04/fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), 0
        self.vy = +6
        self.bound = random.randint(50, HEIGHT/2)  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル

    def update(self):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.centery += self.vy



    def get_direction(self) -> tuple[int, int]:
        return self.get_direction
    def toggle_high_speed_mode(self):
        self.high_speed_mode = not self.high_speed_mode



class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.score = 0
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def score_up(self, add):
        self.score += add

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        screen.blit(self.image, self.rect)

class Shield(pg.sprite.Sprite):
    """
    爆弾を防ぐシールドに関するクラス 
    """
    def __init__(self, bird: Bird, life:int):
        super().__init__()
        vx, vy = bird.get_direction()  # こうかとんの向き
        angle = math.degrees(math.atan2(-vy, vx)) 
        self.image = pg.Surface((20, 2*bird.rect.height))
        self.image = pg.transform.rotozoom(self.image, angle, 1.0)
        pg.draw.rect(self.image, (0, 0, 0), (0, 0, 20, 2*bird.rect.height))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*vx
        self.life = life
     
    def update(self):
        self.life -= 1
        if(self.life <= 0):
            self.kill()
            

class Gravity(pg.sprite.Sprite):
    """
    重力球に関するクラス
    """
    def __init__(self, bird: Bird, size: int, life: int):
        """
        重力球の円Surfaceと対応するRectを生成する
        引数1 bird：こうかとん
        引数2 size：重力球の半径
        引数3 life：発動時間
        """
        super().__init__()
        # self.size = size
        self.image = pg.Surface((2*size, 2*size))
        self.image.set_alpha(200)
        self.image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.image, (10, 10, 10), (size, size), size)
        self.rect = self.image.get_rect(center=bird.rect.center)
        # self.rect.center = bird.rect.centerSs
        self.life = life

    def update(self):
        """
        発動時間を1減算し，0未満になったらkill
        """

class NeoGravity(pg.sprite.Sprite):
    """
    重力場に関するクラス
    """
    def __init__(self, life):
        super().__init__()
        self.image = pg.Surface((WIDTH,HEIGHT))
        self.image.set_alpha(150)
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        pg.draw.rect(self.image,(10,10,10),pg.Rect(0,0,WIDTH,HEIGHT))
        self.life = life        
    def update(self):

        self.life -= 1
        if self.life < 0:
            self.kill()


    def get_score(self): # int型のスコアを返す関数
        return int(self.score)

class Gravity(pg.sprite.Sprite):
    """
    追加機能５の重力球に関するクラス
    こうかとんを中心に重力球を発生させる
    """
    def __init__(self, bird, size, life):
        super().__init__()
        RGBA = (0, 0, 0, 100) # 重力球の色を透過度100の黒に設定
        self.image = pg.Surface((2*size, 2*size), pg.SRCALPHA) # pg.SRCALPHAでSurfaceを透過に対応させる
        self.rect = pg.draw.circle(self.image, RGBA, (size, size), size) # 新しく作ったself.imageというSurfaceの(size,size)の位置に円を生成
        self.rect.center = bird.rect.center # 重力球の中心をbirdの中心に設定
        self.image.set_colorkey((255,255,255)) # 黒を透過する
        self.life = life

    def update(self): # 重力球のlifeを１ずつ減算し、0未満になったらkill()
        self.life -= 1
        if self.life < 0:
            self.kill()




def main():
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("ex04/fig/pg_bg.jpg")
    score = Score()
    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    gravities = pg.sprite.Group() # Gravityグループを追加する

    shields = pg.sprite.Group()

    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    gras = pg.sprite.Group()
    neo = pg.sprite.Group()
    shields = pg.sprite.Group()

    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()            
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 
            if event.type == pg.KEYDOWN and event.key == pg.K_CAPSLOCK and len(shields) == 0 and score.score >= 50:
                shields.add(Shield(bird, 400))
                score.score -= 50
                beams.add(Beam(bird)) 
            if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT:
                bird.speed = 20
            elif event.type == pg.KEYUP and event.key == pg.K_LSHIFT:
                bird.speed = 10
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.add(Beam(bird, 0))
                
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE and key_lst[pg.K_LSHIFT]:
                beams.add(NeoBeam(bird, 5).gen_beams())     
                beams.add(Beam(bird))
                if key_lst[pg.K_LSHIFT]:  # 左シフトが押されているなら
                    neobeam = NeoBeam(bird, 5).gen_beams()  # Beamのリストを入れて、forを回してadd
                    for b in neobeam:
                        beams.add(b)

            if event.type == pg.KEYDOWN and event.key == pg.K_TAB \
                and score.get_score() > 50\
                and len(gravities) == 0: # TABキーを押している　かつ　スコアが50より大きい　かつ　gravitiesグループに他にgravityインスタンスがない
                score.score_up(-50)
                gravities.add(Gravity(bird, 200, 500)) # size（半径）を200、life（発動時間）を500に設定したGravityをgravitiesグループに追加

            if event.type == pg.KEYDOWN and event.key == pg.K_RSHIFT:
                if  score.score >= 10:
                    bird.change_state("hyper",500) #コウカトンの状態をハイパーにする
                    score.score -= 100 # スコアを１００消費する
                 
            if event.type == pg.KEYDOWN and event.key == pg.K_CAPSLOCK and len(shields) == 0:
                if score.score > 50:
                    shields.add(Shield(bird,400))
                    score.score_up(-50)

            """
            重力球処理
            """
            if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                # スコアが200以上の場合のみ重力球を発動
                if score.score >= 200:
                    gravity = Gravity(bird, 200, 500)
                    gras.add(gravity)

            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                if score.score >= 200:
                    neo.add(NeoGravity(400))
                    score.score_up(-200)            
        
        screen.blit(bg_img, [0, 0])

        if tmr%200== 0:  # 200フレームに1回，敵機を出現させる
            emys.add(Enemy())

        for emy in emys:
            if emy.state == "stop" and tmr%emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                bombs.add(Bomb(emy, bird))


        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():#複数の衝突判定

            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.score_up(10)  # 10点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト


        for bomb in pg.sprite.groupcollide(bombs, gras, True, False).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.score_up(1)  # 1点アップ
            

        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():#複数の衝突判定
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.score_up(1)  # 1点アップ
            
        for bomb in pg.sprite.groupcollide(bombs, neo, True, False).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.score_up(1)  # 1点アップ

        for bomb in pg.sprite.groupcollide(bombs, shields, True, False).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.score_up(1)  # 1点アップ

        
        for bomb in pg.sprite.groupcollide(bombs, gravities, True, False).keys(): # bombとgravitiesの衝突判定。bombのみ消える
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.score_up(1) # 1点アップ
    
        gravities.update()
        gravities.draw(screen)
        
        for emy in pg.sprite.groupcollide(emys, neo, True, False):
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.score_up(10)  # 10点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト

        for bomb in pg.sprite.spritecollide(bird, bombs, True):
            if bird.state == "hyper":
                exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                score.score_up(1)

            else:#nomalモードの時
                bird.change_img(8, screen) # こうかとん悲しみエフェクト
                score.update(screen)
                pg.display.update()
                time.sleep(2)
                return
                

        for bomb in pg.sprite.spritecollide(bird, bombs, True):#衝突判定
            if bird.state == "normal":
                bird.change_img(8,screen)# こうかとん悲しみエフェクト
                score.update(screen)
                pg.display.update()
                time.sleep(2)
                return 
            if bird.state == "hyper":
                exps.add(Explosion(bomb,50))#爆発エフェクト
                score.score_up(1)#1点アップ
                #bird.change_img(6,screen)# こうかとん喜びエフェクト
                score.update(screen)
                pg.display.update()

        bird.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        emys.update()
        emys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        shields.update()
        shields.draw(screen)
        score.update(screen)
        gras.update()
        gras.draw(screen)
        neo.update()
        neo.draw(screen)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()