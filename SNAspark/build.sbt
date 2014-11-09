name := "SNAspark"

version := "1.0"

scalaVersion := "2.10.4-local"

scalaHome := Some(file("/usr/local/Cellar/scala210/2.10.4/libexec/"))

libraryDependencies += "org.apache.spark" %% "spark-core" % "1.1.0"

libraryDependencies += "org.apache.spark" %% "spark-sql" % "1.1.0"

resolvers += "Akka Repository" at "http://repo.akka.io/releases/"
