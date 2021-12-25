import discord, os, random, datetime, asyncio, requests, io, aiohttp, asyncpg 
from discord.ext import commands
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)
random.seed()
non_admin_commands = ["numbers", "complete", "connect4", "inspirobot"]
# --------------------------------- START OF NUMBERS GAME -----------------------------------
class NumbersGame:
  def setup(self, channel):
    self._correct = []
    self._leaderboard = {}
    self._last_time = 0
    self._channel = channel

  def __init__(self, channel):
    self.setup(channel)

  def add_correct(self, num):
    self._correct.append(num)

  def add_leader(self, key, value):
    self._leaderboard[key] = value if key not in self._leaderboard else value + self._leaderboard[key]

  async def create_numgame_msg(self, channel):
    msg = "The scores are...\n"
    for entry in sorted(self._leaderboard.items(), key=lambda x: x[1], reverse = True):  
      msg += "{} got a score of {:.1f}.\n".format(entry[0], entry[1])
    await channel.send(msg)
    num_game_array.remove(self)

  async def send_numgame(self, channel):
    for i in range(10):
      leader_old = self._leaderboard.copy()
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
      self._last_time = datetime.datetime.now()
      self.add_correct(correct_ans)
      await asyncio.sleep(15)
      leader_new = self._leaderboard.copy()
      if leader_new == leader_old:
    
        await channel.send("Timing out because nobody responded...")
        break
    await self.create_numgame_msg(channel)
  # -------------------------- GETTERS ----------------------------------------
  def get_last_time(self):
    return self._last_time
  def get_correct(self):
    return self._correct 
  def get_channel(self):
    return self._channel 

num_game_array = []

def find_num_game(channel):
  for game in num_game_array:
    if game.get_channel() == channel:
      return game
  return 0

def new_num_game(channel):
  num_game_array.append(NumbersGame(channel))
  return num_game_array[-1]
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
  def full(self):
    if len(self._win_dict['red']) + len(self._win_dict['yellow']) == 42:
      return "Nobody"
  def get_turn(self):
    return  self._turn
  def get_boardID(self):
    return  self._boardID
  def get_emojis(self):
    return  self._emojis 
  # ----------------------------- END OF CONNECT4 OBJECT ----------------
      
C4_array = []

def find_game_c4(payload):
  for game in C4_array:
    if (payload.message_id == game.get_boardID().id):
      return game
  return 0

def new_game_c4():
  C4_array.append(Connect4())
  return C4_array[-1]

def add_excl(string): #helper for working with users
  return "@!".join(string.split('@'))

class MemberError(Exception):
  pass

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  await bot.process_commands(message)
 
bot.remove_command("help")
@bot.command()
async def help(ctx):
  embedVar = discord.Embed(title="Hi, I'm RBot and I do a few fun things in Discord.")
  embedVar.add_field(name="Number Game", value="Find out who is the fastest at math! Type .numbers to start.", inline=False)
  embedVar.add_field(name="Message Completer", value="Type .complete followed by the beginning of a sentence, and have DeepAI complete the sentence.", inline=False)
  embedVar.add_field(name="Connect 4", value="Type .connect4 followed by a mention of someone else to start a connect 4 game with the other person.", inline=False)
  embedVar.add_field(name="Inspirobot", value="Type .inspirobot to get an artificially intelligent inspirational quote from Inspirobot.", inline=False)
  await ctx.send(embed=embedVar)
 
@bot.command()
async def numbers(ctx):
  NumGameState = new_num_game(ctx.message.channel)
  await ctx.send("Starting numbers game!\nTo answer, type .n followed by your answer.")
  await NumGameState.send_numgame(ctx.message.channel)

@bot.command()
async def n(ctx):
  NumGameState = find_num_game(ctx.message.channel)
  if NumGameState:
    time_delta = datetime.datetime.now() - NumGameState.get_last_time() # Calculating score
    secs = time_delta.total_seconds()
    try: 
      answer = int(ctx.message.content.split()[1])
    except (ValueError, IndexError):
      await ctx.send("Please enter .n followed by a numerical answer (only digits please).")
    else:
      score = 100/secs if answer == NumGameState.get_correct()[-1] else 0
      NumGameState.add_leader(ctx.message.author.mention, score)

@bot.command()
async def complete(ctx):
  try:
    raw = requests.post("https://api.deepai.org/api/text-generator",
    data={
      'text': " ".join(ctx.message.content.split()[1:]),
    },
    headers={'Api-Key': os.getenv('TOKEN2')})
    processed = raw.json()["output"].split('.')[0] + '.' #Get the response and stop when you find a period
  except (IndexError, AttributeError, KeyError):
    processed = "Please enter .complete followed by a word or sequence of words."
  finally:
    await ctx.send(processed)

@bot.command()
async def connect4(ctx): #initializing connect 4 state
  auth_mention = add_excl(ctx.message.author.mention)
  try:
    other_player = ctx.message.content.split()[1]
    if other_player == auth_mention or not ctx.message.guild.get_member(int(other_player[3:-1])):
      raise MemberError
    Connect4State = new_game_c4()
    Connect4State.setup(auth_mention, other_player)
    msg = Connect4State.send_c4_board()
    boardID = await ctx.send(msg)
    Connect4State.set_boardID(boardID)
    for emoji in Connect4State.get_emojis():
      await Connect4State.get_boardID().add_reaction(emoji)
  except (IndexError, MemberError, ValueError):
    await ctx.send("Please type .connect4 followed by a space, and then mention someone else to start a game")
# #----------------------- INSPIROBOT ----------------------------------------------  

@bot.command()
async def inspirobot(ctx):
    link = "https://inspirobot.me/api?generate=true"
    f = requests.get(link)
    imgurl=f.text
    async with aiohttp.ClientSession() as session:
      async with session.get(imgurl) as resp:
        if resp.status != 200:
            return await ctx.send('Could not download file...')
        data = io.BytesIO(await resp.read())
        await ctx.send(file=discord.File(data, 'cool_image.png'))

@bot.command()
async def deactivate(ctx):
  current_server = ctx.message.guild
  ctx.send(current_server)
  print(current_server  )
  comm_to_deactivate = ctx.message.content.split()[1]
  if comm_to_deactivate not in non_admin_commands:
    await ctx.send("Sorry you cannot deactivate this command.")
    return
  database_url = os.environ.get('DATABASE_URL', None)
  conn = await asyncpg.connect(database_url)
  await conn.execute('UPDATE servers SET forbidden=$2 WHERE id=$1', current_server, array_append(forbidden, comm_to_deactivate))
  await conn.close()
  
@bot.event
async def on_raw_reaction_add(payload):
  Connect4State = find_game_c4(payload)
  if Connect4State: #if there's a c4 game going on...
    pay_mention = add_excl(payload.member.mention)
    if (pay_mention == Connect4State.get_turn()) and (payload.emoji.name in Connect4State.get_emojis()): # if the correct person responds with a valid answer
      err_code = Connect4State.add_to_board(payload.emoji.name, pay_mention)
      if err_code == 0:# if adding the chip was successful
        Connect4State.switch_turn()
        new_msg = Connect4State.send_c4_board()
        won = Connect4State.check_for_win()
        full = Connect4State.full()
        if won or full:
          winner = won if won else full
          new_msg = new_msg + '\n{} won!'.format(winner)
          await Connect4State.get_boardID().edit(content=new_msg)
          C4_array.remove(Connect4State)
        else:
          await Connect4State._boardID.edit(content=new_msg)
    if Connect4State and await bot.fetch_user(pay_mention[3:-1]) != bot.user and Connect4State.get_boardID().id == payload.message_id: #if someone other than the bot adds a reaction to the connect 4 game
      await Connect4State.get_boardID().remove_reaction(payload.emoji.name, await bot.fetch_user(pay_mention[3:-1]))

bot.run(os.getenv('TOKEN1'))