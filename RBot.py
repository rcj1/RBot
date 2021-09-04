import discord, os, random, datetime, asyncio, requests 
client = discord.Client()
random.seed()

class NumbersGame:
  def setup(self):
    self.correct = []
    self.leaderboard = {}
    self.startTime = 0
  def __init__(self):
    self.setup()
  def addCorrect(self, num):
    self.correct.append(num)
  def addLeader(self, key, value):
    self.leaderboard[key] = value if key not in self.leaderboard else value + self.leaderboard[key]
  def start(self):
    self.startTime = datetime.datetime.now()

GameState = NumbersGame()

class Connect4:
  def setup(self, user1, user2):
    if random.randrange(2) == 0:
      self.red = user1
      self.yellow = user2
    else:
      self.red = user2
      self.yellow = user1
    # red goes first
    self.turn = self.red
    self.board = [[◼️◼️◼️◼️◼️◼️][◼️◼️◼️◼️◼️◼️][◼️◼️◼️◼️◼️◼️][◼️◼️◼️◼️◼️◼️][◼️◼️◼️◼️◼️◼️][◼️◼️◼️◼️◼️◼️][◼️◼️◼️◼️◼️◼️]]
  def __init__(self):
    self.setup('', '')
  def switchTurn(self):
    self.turn = self.yellow if self.turn == self.red else self.red
    # if the previous turn was red, the current turn is yellow and vice versa

Connect4State = Connect4()

async def createNumGameMsg(channel):
  msg = "The scores are...\n"
  for entry in sorted(GameState.leaderboard.items(), key=lambda x: x[1], reverse = True):  
    msg += "{} got a score of {:.2f}.\n".format(entry[0], entry[1])
  await channel.send(msg)
  GameState.setup()

async def sendNumGame(channel):
  for i in range(10):
    coinToss = random.randrange(2)
    if coinToss == 0:
      rand1 = random.randrange(1, 200)
      rand2 = random.randrange(1, 200)
      msg = str(rand1) + " + " + str(rand2) + " =?"
      correctAns = rand1 + rand2
    else:
      rand1 = random.randrange(1, 10)
      rand2 = random.randrange(1, 100)
      msg = str(rand1) + " x " + str(rand2) + " =?"
      correctAns = rand1 * rand2
    await channel.send(msg)
    GameState.addCorrect(correctAns)
    await asyncio.sleep(15)
  await createNumGameMsg(channel)


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  elif message.content == ".help":
    await message.channel.send("Hi, I'm RBot and I do a few fun things in Discord.\n\nNumber Game\n--------\n\nType .numbers to start a number game. You will be given ten arithmetic questions with 15 seconds to solve each one. Whoever gets the most questions right in the least amount of time wins. Specifically, your score for each question is 0 if you answer incorrectly, and 100/response time (seconds) if you answer correctly. The scores for each question are then summed.\n\nMessage Completer\n--------\n\nType .complete followed by the beginning of a sentence, and have DeepAI complete the sentence.")
  # ---------------------- NUMBERS GAME ---------------------------------------------------
  elif message.content == ".numbers":
    GameState.start()
    await message.channel.send("Starting numbers game!\nTo answer, type .n followed by your answer.")
    await sendNumGame(message.channel)

  elif message.content.startswith(".n") and len(GameState.correct) > 0:
    timeDelta = datetime.datetime.now() - GameState.startTime # Calculating score
    secs = timeDelta.total_seconds() % 15 
    answer = int(message.content.split()[1])
    score = 100/secs if answer == GameState.correct[-1] else 0
    GameState.addLeader(message.author.mention, score)
  # ------------------------ SENTENCE COMPLETION -----------------------------------------
  elif message.content.startswith(".complete"):
    raw = requests.post("https://api.deepai.org/api/text-generator",
    data={
      'text': " ".join(message.content.split()[1:]),
    },
    headers={'Api-Key': os.getenv('TOKEN2')})
    processed = raw.json()["output"].split('.')[0] + '.' #Get the response and stop when you find a period
    await message.channel.send(processed)
  # ------------------------CONNECT 4------------------------------------------------------
  elif message.content.startswith(".connect4"):
    Connect4State.setup(message.author.mention, message.content.split()[1])
    print(Connect4State)
client.run(os.getenv('TOKEN1'))