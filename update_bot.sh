kek=`ps -ef | grep "otr_bot/bot.py" | grep -v grep`
if ! [ -z "$kek" ]
then
  echo "Bot is running. First stop bot"
  exit 1
fi

git config pull.ff only
git pull