import json
import random
import sqlite3 as sql
import os.path

from flask import Flask, render_template, request

app = Flask(__name__, static_folder='templates/static/')

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/sign_up", methods=['POST'])
def sign_up():
    username = request.form['username']
    password = request.form['password']
    con = sql.connect('db.sqlite3')
    cur = con.cursor()
    cur.execute("insert into user(username,password) values (?,?)", (username, password))
    con.commit()
    cur.execute("select last_insert_rowid()")
    user_id = cur.fetchone()[0]
    data = {'result': True, 'id': user_id, 'username': username}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/sign_in", methods=['POST'])
def sign_in():
    username = request.form['username']
    password = request.form['password']
    con = sql.connect('db.sqlite3')
    cur = con.cursor()
    cur.execute("select * from  user where username = ? and password = ?", (username, password))
    row = cur.fetchone()
    if row:
        user_id = row[0]
    else:
        user_id = 0
    data = {'result': True if row else False, 'id': user_id}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/next_word', methods=['POST'])
def next_word():
    con = sql.connect('db.sqlite3')
    con.row_factory = sql.Row
    cur = con.cursor()
    word_id = random.randint(1, 478)
    cur.execute("select word from words where id = ?", [word_id])
    row = cur.fetchone()
    word = row[0]
    sorted_word = sorted(word)
    sorted_word = ''.join(sorted_word)
    data = {'word': sorted_word}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/check", methods=['POST'])
def check():
    word = request.form['word']
    con = sql.connect('db.sqlite3')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select count(*) from words where word = ?", [word])
    row = cur.fetchone()
    number = row[0]
    data = {'result': True if number > 0 else False}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/save", methods=['POST'])
def save():
    user_id = request.form['id']
    words = request.form['words']
    number = request.form['number']
    con = sql.connect('db.sqlite3')
    cur = con.cursor()
    save_sql = '''
        insert into game(user_id, words, number, time) values (?,?, ?, datetime('now', 'localtime'))
        '''
    cur.execute(save_sql, (user_id, words, number))
    con.commit()
    data = {'result': True}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/statistics", methods=['POST'])
def statistics():
    user_id = request.form['id']

    # total_played
    sql_1 = '''
        select count(*)
        from game
        where user_id = ?
        '''

    # max_number, max_number_time, average_number
    sql_2 = '''
        select max(number), time, avg(number)
        from game
        where user_id = ?
        '''

    # world_rank
    sql_3 = '''
        select rank
        from (SELECT u.id        AS uid,
                     rank() over (
                         order by MAX(number) desc
                         )       AS rank
              FROM game g
                       join user u
                            on g.user_id = u.id
              GROUP BY u.id)
        where uid = ?
        '''

    # no1_username, no1_max_number
    sql_4 = '''
        select u.username, max(g.number)
        from user u
                 join game g
                      on u.id = g.user_id
        group by u.id
        order by max(g.number) desc
        limit 1;
        '''

    con = sql.connect('db.sqlite3')
    cur = con.cursor()

    cur.execute(sql_1, [user_id])
    row = cur.fetchone()
    total_played = row[0]

    cur.execute(sql_2, [user_id])
    row = cur.fetchone()
    max_number = row[0]
    max_number_time = row[1]
    average_number = int(row[2])

    cur.execute(sql_3, [user_id])
    row = cur.fetchone()
    world_rank = row[0]

    cur.execute(sql_4)
    row = cur.fetchone()
    no1_username = row[0]
    no1_max_number = row[1]

    data = {
        'total_played': total_played,
        'max_number': max_number,
        'max_number_time': max_number_time,
        'average_number': average_number,
        'world_rank': world_rank,
        'no1_username': no1_username,
        'no1_max_number': no1_max_number
    }

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


def init_db():
        con = sql.connect('db.sqlite3')
        cur = con.cursor()

        sql_user = '''
        CREATE TABLE user(
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
        '''
        sql_word = '''
        CREATE TABLE words(
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            word char(4)
        )
        '''
        sql_game = '''
        CREATE TABLE game(
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES user,
            words   TEXT,
            number  INTEGER,
            time    TEXT
        );
        '''

        sql_insert_user = '''
            BEGIN TRANSACTION; 
            INSERT INTO user (id, username, password) VALUES (1, 'test_user_1', 'test_password_1');
            INSERT INTO user (id, username, password) VALUES (2, 'test_user_2', 'test_password_2');
            COMMIT;
        '''


        cur.execute(sql_user)
        cur.execute(sql_word)
        cur.execute(sql_game)

        words = [(1,'ABLE'),(2,'AGED'),(3,'ALSO'),(4,'AREA'),(5,'ARMY'),(6,'AWAY'),(7,'BABY'),(8,'BACK'),(9,'BALL'),(10,'BAND'),(11,'BANK'),(12,'BASE'),(13,'BATH'),(14,'BEAR'),(15,'BEAT'),(16,'BEEN'),(17,'BEER'),(18,'BELL'),(19,'BELT'),(20,'BEST'),(21,'BILL'),(22,'BIRD'),(23,'BLUE'),(24,'BOAT'),(25,'BODY'),(26,'BOOK'),(27,'BOOM'),(28,'BORN'),(29,'BOSS'),(30,'BOTH'),(31,'BOWL'),(32,'BULK'),(33,'BURN'),(34,'BUSH'),(35,'BUSY'),(36,'CALL'),(37,'CALM'),(38,'CAME'),(39,'CAMP'),(40,'CARD'),(41,'CARE'),(42,'CASE'),(43,'CASH'),(44,'CAST'),(45,'CELL'),(46,'CHAT'),(47,'CHIP'),(48,'CITY'),(49,'CLUB'),(50,'COAL'),(51,'COAT'),(52,'CODE'),(53,'COLD'),(54,'COME'),(55,'COOK'),(56,'COOL'),(57,'COPE'),(58,'COPY'),(59,'CORE'),(60,'COST'),(61,'CREW'),(62,'CROP'),(63,'DARK'),(64,'DATA'),(65,'DATE'),(66,'DAWN'),(67,'DAYS'),(68,'DEAL'),(69,'DEAN'),(70,'DEAR'),(71,'DEEP'),(72,'DENY'),(73,'DESK'),(74,'DIAL'),(75,'DICK'),(76,'DIET'),(77,'DISC'),(78,'DISK'),(79,'DOES'),(80,'DONE'),(81,'DOOR'),(82,'DOSE'),(83,'DOWN'),(84,'DRAW'),(85,'DREW'),(86,'DROP'),(87,'DUAL'),(88,'DUKE'),(89,'DUST'),(90,'DUTY'),(91,'EACH'),(92,'EARN'),(93,'EASE'),(94,'EAST'),(95,'EASY'),(96,'EDGE'),(97,'ELSE'),(98,'EVEN'),(99,'EVER'),(100,'EXIT'),(101,'FACE'),(102,'FACT'),(103,'FAIR'),(104,'FALL'),(105,'FARM'),(106,'FAST'),(107,'FATE'),(108,'FEED'),(109,'FEEL'),(110,'FEET'),(111,'FELT'),(112,'FILE'),(113,'FILL'),(114,'FILM'),(115,'FIND'),(116,'FINE'),(117,'FIRE'),(118,'FIRM'),(119,'FISH'),(120,'FIVE'),(121,'FLAT'),(122,'FLOW'),(123,'FOOD'),(124,'FOOT'),(125,'FORD'),(126,'FORM'),(127,'FORT'),(128,'FOUR'),(129,'FREE'),(130,'FROM'),(131,'FUEL'),(132,'FULL'),(133,'FUND'),(134,'GAIN'),(135,'GAME'),(136,'GATE'),(137,'GAVE'),(138,'GEAR'),(139,'GENE'),(140,'GIFT'),(141,'GIRL'),(142,'GIVE'),(143,'GLAD'),(144,'GOAL'),(145,'GOES'),(146,'GOLD'),(147,'GOLF'),(148,'GONE'),(149,'GOOD'),(150,'GRAY'),(151,'GREW'),(152,'GREY'),(153,'GROW'),(154,'GULF'),(155,'HAIR'),(156,'HALF'),(157,'HALL'),(158,'HAND'),(159,'HANG'),(160,'HARD'),(161,'HAVE'),(162,'HEAD'),(163,'HEAR'),(164,'HEAT'),(165,'HELD'),(166,'HELL'),(167,'HELP'),(168,'HERE'),(169,'HERO'),(170,'HIGH'),(171,'HILL'),(172,'HIRE'),(173,'HOLD'),(174,'HOLE'),(175,'HOLY'),(176,'HOME'),(177,'HOPE'),(178,'HOST'),(179,'HOUR'),(180,'HUGE'),(181,'HUNG'),(182,'HUNT'),(183,'HURT'),(184,'IDEA'),(185,'INCH'),(186,'INTO'),(187,'IRON'),(188,'ITEM'),(189,'JACK'),(190,'JANE'),(191,'JEAN'),(192,'JOHN'),(193,'JOIN'),(194,'JUMP'),(195,'JURY'),(196,'JUST'),(197,'KEEN'),(198,'KEEP'),(199,'KENT'),(200,'KEPT'),(201,'KICK'),(202,'KILL'),(203,'KIND'),(204,'KING'),(205,'KNEE'),(206,'KNEW'),(207,'KNOW'),(208,'LACK'),(209,'LADY'),(210,'LAID'),(211,'LAKE'),(212,'LAND'),(213,'LANE'),(214,'LAST'),(215,'LATE'),(216,'LEAD'),(217,'LEFT'),(218,'LESS'),(219,'LIFE'),(220,'LIFT'),(221,'LIKE'),(222,'LINE'),(223,'LINK'),(224,'LIST'),(225,'LIVE'),(226,'LOAD'),(227,'LOAN'),(228,'LOCK'),(229,'LOGO'),(230,'LONG'),(231,'LOOK'),(232,'LORD'),(233,'LOVE'),(234,'LUCK'),(235,'MADE'),(236,'MAIL'),(237,'MAIN'),(238,'MAKE'),(239,'MALE'),(240,'MANY'),(241,'MARK'),(242,'MASS'),(243,'MATT'),(244,'MEAL'),(245,'MEAN'),(246,'MEAT'),(247,'MEET'),(248,'MENU'),(249,'MERE'),(250,'MIKE'),(251,'MILE'),(252,'MILK'),(253,'MILL'),(254,'MIND'),(255,'MINE'),(256,'MISS'),(257,'MODE'),(258,'MOOD'),(259,'MOON'),(260,'MORE'),(261,'MOST'),(262,'MOVE'),(263,'MUCH'),(264,'MUST'),(265,'NAME'),(266,'NAVY'),(267,'NEAR'),(268,'NECK'),(269,'NEED'),(270,'NEWS'),(271,'NEXT'),(272,'NICE'),(273,'NICK'),(274,'NINE'),(275,'NONE'),(276,'NOSE'),(277,'NOTE'),(278,'OKAY'),(279,'ONCE'),(280,'ONLY'),(281,'ONTO'),(282,'OPEN'),(283,'ORAL'),(284,'OVER'),(285,'PACE'),(286,'PACK'),(287,'PAGE'),(288,'PAID'),(289,'PAIR'),(290,'PALM'),(291,'PARK'),(292,'PART'),(293,'PASS'),(294,'PAST'),(295,'PATH'),(296,'PEAK'),(297,'PICK'),(298,'PINK'),(299,'PIPE'),(300,'PLAN'),(301,'PLAY'),(302,'PLOT'),(303,'PLUG'),(304,'PLUS'),(305,'POLL'),(306,'POOL'),(307,'PORT'),(308,'POST'),(309,'PULL'),(310,'PURE'),(311,'PUSH'),(312,'RACE'),(313,'RAIL'),(314,'RAIN'),(315,'RANK'),(316,'RARE'),(317,'RATE'),(318,'READ'),(319,'REAL'),(320,'REAR'),(321,'RELY'),(322,'RENT'),(323,'REST'),(324,'RICE'),(325,'RICH'),(326,'RIDE'),(327,'RING'),(328,'RISE'),(329,'RISK'),(330,'ROAD'),(331,'ROCK'),(332,'ROLE'),(333,'ROLL'),(334,'ROOF'),(335,'ROOM'),(336,'ROOT'),(337,'ROSE'),(338,'RULE'),(339,'RUSH'),(340,'RUTH'),(341,'SAFE'),(342,'SAID'),(343,'SAKE'),(344,'SALE'),(345,'SALT'),(346,'SAME'),(347,'SAND'),(348,'SAVE'),(349,'SEAT'),(350,'SEED'),(351,'SEEK'),(352,'SEEM'),(353,'SEEN'),(354,'SELF'),(355,'SELL'),(356,'SEND'),(357,'SENT'),(358,'SEPT'),(359,'SHIP'),(360,'SHOP'),(361,'SHOT'),(362,'SHOW'),(363,'SHUT'),(364,'SIDE'),(365,'SIGN'),(366,'SITE'),(367,'SIZE'),(368,'SKIN'),(369,'SLIP'),(370,'SLOW'),(371,'SNOW'),(372,'SOFT'),(373,'SOIL'),(374,'SOLD'),(375,'SOLE'),(376,'SOME'),(377,'SONG'),(378,'SOON'),(379,'SORT'),(380,'SOUL'),(381,'SPOT'),(382,'STAR'),(383,'STAY'),(384,'STEP'),(385,'STOP'),(386,'SUCH'),(387,'SUIT'),(388,'SURE'),(389,'TAKE'),(390,'TALE'),(391,'TALK'),(392,'TALL'),(393,'TANK'),(394,'TAPE'),(395,'TASK'),(396,'TEAM'),(397,'TECH'),(398,'TELL'),(399,'TEND'),(400,'TERM'),(401,'TEST'),(402,'TEXT'),(403,'THAN'),(404,'THAT'),(405,'THEM'),(406,'THEN'),(407,'THEY'),(408,'THIN'),(409,'THIS'),(410,'THUS'),(411,'TILL'),(412,'TIME'),(413,'TINY'),(414,'TOLD'),(415,'TOLL'),(416,'TONE'),(417,'TONY'),(418,'TOOK'),(419,'TOOL'),(420,'TOUR'),(421,'TOWN'),(422,'TREE'),(423,'TRIP'),(424,'TRUE'),(425,'TUNE'),(426,'TURN'),(427,'TWIN'),(428,'TYPE'),(429,'UNIT'),(430,'UPON'),(431,'USED'),(432,'USER'),(433,'VARY'),(434,'VAST'),(435,'VERY'),(436,'VICE'),(437,'VIEW'),(438,'VOTE'),(439,'WAGE'),(440,'WAIT'),(441,'WAKE'),(442,'WALK'),(443,'WALL'),(444,'WANT'),(445,'WARM'),(446,'WASH'),(447,'WAVE'),(448,'WAYS'),(449,'WEAR'),(450,'WEEK'),(451,'WELL'),(452,'WENT'),(453,'WERE'),(454,'WEST'),(455,'WHAT'),(456,'WHEN'),(457,'WHOM'),(458,'WIDE'),(459,'WIFE'),(460,'WILD'),(461,'WILL'),(462,'WIND'),(463,'WINE'),(464,'WING'),(465,'WIRE'),(466,'WISE'),(467,'WISH'),(468,'WITH'),(469,'WOOD'),(470,'WORD'),(471,'WORE'),(472,'WORK'),(473,'YARD'),(474,'YEAH'),(475,'YEAR'),(476,'YOUR'),(477,'ZERO'),(478,'ZONE')]

        cur.executemany('insert into words(id, word) VALUES(?, ?)', words)

        con.commit()
        con.close()


if __name__ == '__main__':
    if os.path.isfile('db.sqlite3'):
        print('db.sqlite3 exist')
    else:
        print('+db.sqlite3 init.')
        init_db()
    app.secret_key = 'PUZZlE'
    app.run(debug=True, host='127.0.0.1')
