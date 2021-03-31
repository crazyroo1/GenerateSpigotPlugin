import os

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


workingDirectory = input("Enter the full path to where you want to generate the plugin files: ")
if workingDirectory[-1] != "/":
    workingDirectory += "/"

if not os.path.exists(workingDirectory) and not os.path.isfile(workingDirectory):
    print("This directory does not exist or is a file, not a directory.")
    print("Check your entry and try again")
    exit(1)

if input("All files in " + workingDirectory + " will be deleted. OK? (y/n): ").lower() == "y":
    for file in os.listdir(workingDirectory):
        os.remove(workingDirectory + file)

group = input("Group (ex: com.crazyroo1): ")
pluginName = input("Plugin Name (CamelCase): ")
author = input("Author: ")
mcVersion = input("Minecraft Version: ")
with open(workingDirectory + "gradle.properties", "w") as gradleProperties:
    gradleProperties.writelines(["group = " + group,
                                 "\npluginName = " + pluginName,
                                 "\nauthor = " + author,
                                 "\nmcVersion = " + mcVersion,
                                 "\napiVersion = 1.15",
                                 "\nversion = 1.0.0",
                                 "\n"])

os.makedirs(workingDirectory + "src/main/java/" + group + "." + pluginName, exist_ok=True)

with open(workingDirectory + "build.gradle", "w") as buildGradle:
    fileContents = """buildscript {{
    repositories {{
        jcenter()
        mavenCentral()
    }}
}}

plugins {{
    id 'com.github.johnrengelman.shadow' version '6.1.0'
    id 'kr.entree.spigradle' version '2.2.3'
    id 'io.freefair.lombok' version '5.3.0'
    id 'java'
    id 'jacoco'
    id 'idea'
}}

apply from: "$rootDir/gradle/jacoco.gradle"
apply from: "$rootDir/gradle/publish.gradle"

if (project.hasProperty("local_script")) {{
    apply from: file(local_script + "/build.local.gradle")
}}

sourceCompatibility = 11
targetCompatibility = 11

ext {{
    mcVersion = project.property("mcVersion")
}}

group project.property("group")

spigot {{
    name = project.property("pluginName")
    authors = [project.property("author")]
    apiVersion = project.property("apiVersion")
    load = STARTUP
    //    depends = ['']
    debug {{
        buildVersion = "{version}"
    }}
}}

compileJava {{
    options.encoding = 'UTF-8'
    options.compilerArgs += ["-parameters"]
    options.fork = true
    options.forkOptions.executable = 'javac'
}}

archivesBaseName = project.property("pluginName")

repositories {{
    mavenCentral()
    jcenter()
    spigot()
    maven {{ url = 'https://jitpack.io' }}
}}

dependencies {{
    compileOnly spigot('{version}')

    //Add dependencies here

    //Test dependencies
    testImplementation 'org.junit.jupiter:junit-jupiter:5.+'
    testImplementation "org.mockito:mockito-core:3.+"
    testImplementation mockBukkit()
    testImplementation 'org.assertj:assertj-core:3.+'
}}

shadowJar {{
    classifier = ''
//    dependencies {{
//        include(dependency('co.aikar:acf-paper:0.5.0-SNAPSHOT'))
//    }}
//    relocate 'co.aikar.commands', "${{packageName}}.acf"
//    relocate 'co.aikar.locales', "${{packageName}}.locales"
}}

tasks.build.dependsOn(shadowJar)
tasks.publish.dependsOn(shadowJar)
tasks.prepareSpigotPlugins.dependsOn(shadowJar)

test {{
    useJUnitPlatform()
    testLogging {{
        events "passed", "skipped", "failed"
    }}
    ignoreFailures = false
}}

processResources {{
    project.properties.put("version", this.version)
    expand project.properties
}}

defaultTasks 'build'
""".format(version=mcVersion)
    buildGradle.write(fileContents)

with open(workingDirectory + "src/main/java/" + group + "." + pluginName + "/" + pluginName + ".java", "w") as pluginClass:
    fileContents = """package {group}.{pluginName};

import kr.entree.spigradle.annotations.PluginMain;
import org.bukkit.event.Listener;
import org.bukkit.plugin.PluginDescriptionFile;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.plugin.java.JavaPluginLoader;

import java.io.File;

@PluginMain
public class {pluginName} extends JavaPlugin implements Listener {{

  public {pluginName}() {{
  }}

  public {pluginName}(
          JavaPluginLoader loader, PluginDescriptionFile description, File dataFolder, File file) {{
    super(loader, description, dataFolder, file);
  }}

  @Override
  public void onEnable() {{
    getServer().getPluginManager().registerEvents(this, this);
    
    // To build and run, select the RunSpigot configuration from the Run Configurations menu: Jar Application/RunSpigot
    // This configuration goes through the entire process listed below
    // If for some reason it is absent, follow the steps below
    
    // To do the initial build and run, run the following gradle tasks from the right hand edge, under Tasks/spigot debug
    // downloadSpigotBuildTools
    // buildSpigot
    // prepareSpigot
    // prepareSpigotPlugins
    // runSpigot
    
    // To do a standard build and run:
    // prepareSpigotPlugins
    // runSpigot
  }}
}}""".format(group=group, pluginName=pluginName)
    pluginClass.write(fileContents)

os.mkdir(workingDirectory + "gradle")
with open(workingDirectory + "gradle/jacoco.gradle", "w") as jacoco:
    jacoco.write("""jacoco { toolVersion = "0.8.2" }

jacocoTestReport {
    reports {
        xml.enabled true
        html.enabled true
    }
}

tasks.check.dependsOn 'jacocoTestReport'""")

with open(workingDirectory + "gradle/publish.gradle", "w") as publish:
    publish.write("""apply plugin: 'maven-publish'

def getBranch() {
    def process = 'git branch --show-current'.execute()
    process.waitFor()
    return process.text.trim()
}

def getHash() {
    def process = 'git rev-parse HEAD'.execute()
    process.waitFor()
    return process.text.trim()
}

java {
    withJavadocJar()
    withSourcesJar()
}

jar {
    manifest {
        attributes (
                'Build-Jdk': "${System.properties['java.vendor']} ${System.properties['java.vm.version']}",
                'Created-By': "Gradle ${gradle.gradleVersion}",
                'Git-Branch': getBranch(),
                'Git-Hash': getHash()
        )
    }
}

publishing {
    publications {
        mavenJava(MavenPublication) {
            from components.java
        }
    }
    repositories {
        maven {
            name = "GitHubPackages"
            url = uri("https://maven.pkg.github.com/${project.findProperty("GITHUB_REPOSITORY")?: System.getenv("GITHUB_REPOSITORY")}")
            credentials {
                username = project.findProperty("gpr.user") ?: System.getenv("GITHUB_ACTOR")
                password = project.findProperty("gpr.key") ?: System.getenv("GITHUB_TOKEN")
            }
        }
    }
}

javadoc {
    if(JavaVersion.current().isJava9Compatible()) {
        options.addBooleanOption('html5', true)
    }
}
""")

os.mkdir(workingDirectory + "gradle/wrapper")
with open(workingDirectory + "gradle/wrapper/gradle-wrapper.properties", "w") as wrapper:
    wrapper.write("""distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-6.3-all.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")

print("Plugin project generated at " + workingDirectory)
print("Open that directory with IntelliJ and code away!")
