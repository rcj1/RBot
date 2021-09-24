import discord, os, random, datetime, asyncio, requests 
client = discord.Client()
random.seed()
# error handling
# we have to first ensure that someone puts a real valid user in the connect 4
# --------------------------------- START OF NUMBERS GAME -----------------------------------
class NumbersGame:
  def setup(self):
    self._correct = []
    self._leaderboard = {}
    self._start_time = 0

  def __init__(self):
    self.setup()

  def add_correct(self, num):
    self._correct.append(num)

  def add_leader(self, key, value):
    self._leaderboard[key] = value if key not in self._leaderboard else value + self._leaderboard[key]

  def start(self):
    self._start_time = datetime.datetime.now()

  async def create_numgame_msg(self, channel):
    msg = "The scores are...\n"
    for entry in sorted(self._leaderboard.items(), key=lambda x: x[1], reverse = True):  
      msg += "{} got a score of {:.2f}.\n".format(entry[0], entry[1])
    await channel.send(msg)
    self.setup()

  async def send_numgame(self, channel):
    for i in range(10):
      coinToss = random.randrange(2)
      if coinToss == 0:
        rand1 = random.randrange(1, 200)
        rand2 = random.randrange(1, 200)
        msg = str(rand1) + " + " + str(rand2) + " =?"
        correct_ans = rand1 + rand2
      else:
        rand1 = random.randrange(1, 10)
        rand2 = random.randrange(1, 100)
        msg = str(rand1) + " x " + str(rand2) + " =?"
        correct_ans = rand1 * rand2
      await channel.send(msg)
      self.add_correct(correct_ans)
      await asyncio.sleep(15)
    await self.create_numgame_msg(channel)
  # -------------------------- GETTERS ----------------------------------------
  def game_on(self):
    return len(self._correct) > 0
  def get_start_time(self):
    return self._start_time  
  def get_correct(self):
    return self._correct 

GameState = NumbersGame()
# ---------------------------- END OF NUMBERS GAME ------------------------------
# ---------------------------- START OF CONNECT 4 -------------------------------
class Connect4: #standard for working with users: use the one with @!
  def setup(self, user1, user2):
    if random.randrange(2) == 0:
      self._red = user1
      self._yellow = user2
    else:
      self._red = user2
      self._yellow = user1
    # red goes first
    self._turn = self._red
    self._boardID = '' # Message object that represents the board
    self._board = [[],[],[],[],[],[],[]]
    self._emojis =['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣']
    self._win_dict = {"red": [], "yellow": []}

  def __init__(self):
    self.setup('', '')

  def switch_turn(self):
    self._turn = self._yellow if self._turn == self._red else self._red
    # if the previous turn was red, the current turn is yellow and vice versa

  def set_boardID(self, boardID): #board ID is the message object
    self._boardID = boardID

  def add_to_board(self, num_emoji, user):
    color_emoji = '🔴' if user == self._red else '🟡'
    color_dict = "red" if user == self._red else "yellow"
    col_index = self._emojis.index(num_emoji) #integer representing the index of the correct column in the larger list board
    col_height = len(self._board[col_index])
    if col_height < 6:
      self._board[col_index].append(color_emoji)
      self._win_dict[color_dict].append((col_index, col_height))
      return 0
    else: # this is an error because you can only have six chips stacked up
      return -1

  def send_c4_board(self):
    #this prints the board
    msg = "{}'s turn\nRed: {}\nYellow: {}\n".format(self._turn, self._red, self._yellow)
    for i in range(6, 0, -1):
      for j in range(7):
        if len(self._board[j]) >= i:
          msg += self._board[j][i-1]
        else:
          msg += '◼️' # blank slots are represented with these black squares
        msg += ' '
      msg += '\n'
    for k in range(7):
      msg += '{} '.format(self._emojis[k])
    return msg

  def check_for_win(self):
    # these for loops loop through all the possible locations of a chip, once for each color.
    # Each all() statement is a winning condition.
    # For example, if all the tuples (x, y) (x, y+1) (x, y+2) (x, y+3) are in the winning dict, that is a vertical win.
    # There are four such statements for the four possible win situations. 
    # These are connected with any() so that if any one is true, you return the color that won.
    for color in ["red", "yellow"]:
      for x in range(7):
        for y in range(6):
          if any([all(tupl in self._win_dict[color] for tupl in [(x, y), (x, y+1), (x, y+2), (x, y+3)]), all(tupl in self._win_dict[color] for tupl in [(x, y), (x+1, y), (x+2, y), (x+3, y)]), all(tupl in self._win_dict[color] for tupl in [(x, y), (x+1, y+1), (x+2, y+2), (x+3, y+3)]), all(tupl in self._win_dict[color] for tupl in [(x, y), (x+1, y-1), (x+2, y-2), (x+3, y-3)])]):
            if color == "red":
              return self._red
            else:
              return self._yellow
    # return the color that won, and return None if nobody won

  # ----------------------------- GETTER FUNCTIONS ----------------------
  def game_on(self):
    return self._boardID != ''
  def get_turn(self):
    return  self._turn
  def get_boardID(self):
    return  self._boardID
  def get_emojis(self):
    return  self._emojis 
  # ----------------------------- END OF CONNECT4 OBJECT ----------------
      

Connect4State = Connect4()

def add_excl(string): #helper for working with users
  return "@!".join(string.split('@'))

# ------------------------------ END OF CONNECT FOUR ------------------------
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  elif message.content == ".help":
    await message.channel.send("Hi, I'm RBot and I do a few fun things in Discord.\n\nNumber Game\n--------\n\nType .numbers to start a number game. You will be given ten arithmetic questions with 15 seconds to solve each one. Whoever gets the most questions right in the least amount of time wins. Specifically, your score for each question is 0 if you answer incorrectly, and 100/response time (seconds) if you answer correctly. The scores for each question are then summed.\n\nMessage Completer\n--------\n\nType .complete followed by the beginning of a sentence, and have DeepAI complete the sentence.\n\nConnect 4\n--------\n\nType .connect4 followed by a mention of someone else to start a connect 4 game with the other person.")
  # ---------------------- NUMBERS GAME ---------------------------------------------------
  elif message.content == ".numbers":
    GameState.start()
    await message.channel.send("Starting numbers game!\nTo answer, type .n followed by your answer.")
    await GameState.send_numgame(message.channel)

  elif message.content.startswith(".n ") and GameState.game_on():
    time_delta = datetime.datetime.now() - GameState.get_start_time() # Calculating score
    secs = time_delta.total_seconds() % 15
    try: 
      answer = int(message.content.split()[1])
    except ValueError:
      message.channel.send("Please enter .n followed by a numerical answer (only digits please).")
    score = 100/secs if answer == GameState.get_correct()[-1] else 0
    GameState.add_leader(message.author.mention, score)
  # ------------------------ SENTENCE COMPLETION -----------------------------------------
  elif message.content.startswith(".complete "):
    try:
      raw = requests.post("https://api.deepai.org/api/text-generator",
      data={
        'text': " ".join(message.content.split()[1:]),
      },
      headers={'Api-Key': os.getenv('TOKEN2')})
      processed = raw.json()["output"].split('.')[0] + '.' #Get the response and stop when you find a period
    except:
      processed = "Please enter .complete followed by a word or sequence of words."
    finally:
      await message.channel.send(processed)
  # ------------------------CONNECT 4------------------------------------------------------
  elif message.content.startswith(".connect4 "): #initializing connect 4 state
    auth_mention = add_excl(message.author.mention)
    Connect4State.setup(auth_mention, message.content.split()[1])
    msg = Connect4State.send_c4_board()
    boardID = await message.channel.send(msg)
    Connect4State.set_boardID(boardID)
    for emoji in Connect4State.get_emojis():
      await Connect4State.get_boardID().add_reaction(emoji)

@client.event
async def on_raw_reaction_add(payload):
  if Connect4State.game_on(): #if there's a c4 game going on...
    pay_mention = add_excl(payload.member.mention)
    if (payload.message_id == Connect4State.get_boardID().id) and (pay_mention == Connect4State.get_turn()) and (payload.emoji.name in Connect4State.get_emojis()): # if the correct person responds with a valid answer
      err_code = Connect4State.add_to_board(payload.emoji.name, pay_mention)
      if err_code == 0:# if adding the chip was successful
        Connect4State.switch_turn()
        new_msg = Connect4State.send_c4_board()
        won = Connect4State.check_for_win()
        if won:
          new_msg = new_msg + '\n{} won!'.format(won)
          await Connect4State.get_boardID().edit(content=new_msg)
          Connect4State.setup('', '')
        else:
          await Connect4State.boardID.edit(content=new_msg)
    if Connect4State.game_on() and await client.fetch_user(pay_mention[3:-1]) != client.user and Connect4State.get_boardID().id == payload.message_id: #if someone other than the bot adds a reaction to the connect 4 game
      await Connect4State.get_boardID().remove_reaction(payload.emoji.name, await client.fetch_user(pay_mention[3:-1]))

client.run(os.getenv('TOKEN1'))