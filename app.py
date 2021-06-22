import modules.dispatcher.command as disp

if __name__ == "__main__":
	live = 1
	while live:
		cmd = input()
		cmd_split = cmd.split(sep=" ")
		live = disp.cmd_dispatch(cmd_split[0], cmd_split[1:])