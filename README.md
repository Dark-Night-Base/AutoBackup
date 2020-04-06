# AutoBackup

Auto backup with *rsync* on Linux

Compatible with [MCDReforged](https://github.com/Fallen-Breath/MCDReforged)

## How to use

- `!!autobk`: Show help
- `!!autobk set [hour]`: Set the interval between backups, 0 to turn it off
- `!!autobk query`: Query the time of the last backup and the interval

## How it works

*AutoBackup* uses **Linux**'s built-in fast incremental file transfer tool *rsync* 
to backup your working_directory, which is set in the `config.yml` 
with the default as `server`.

You will find a folder called `back-up` in your working_directory, with two backups inside. 

The backup is made when a player go offline and last backup is made before more than 1 hour.
Here "1 hour" is an interval which you can set with `!!autobk set [hour]`. 
However, this interval will be reset to "1" as long as you reload the plugin or restart the MCDR.
