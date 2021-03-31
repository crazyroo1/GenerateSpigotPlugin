# GenerateSpigotPlugin
Simple python program to generate a template Minecraft Spigot plugin project 

Run `python3 GenerateSpigotPlugin.py` to start the process. You'll be asked for the following information:

- Full path
  - This should be the full path to a directory that exists and is empty
  - This will be the root folder of where everything is generated
  - If this directory does not exist, an error will be thrown and execution will halt
    
- Group
    - This is the first part of your package
    - Ex: com.crazyroo1
    
- Plugin Name
    - This is your plugin name
    - This will be filled into the Java class, as well as into other various areas
    - This should be CamelCase as is standard Java style
    - This will also be the last part of the package
        - Ex: A plugin named `MyPlugin` with a group `com.crazyroo1` will be in a package `com.crazyroo1.MyPlugin`
    
- Author
    - Your name
    
- Minecraft Version
    - Version of Minecraft your plugin is built for, as well as the API version your plugin targets
    - Ex: 1.16.5