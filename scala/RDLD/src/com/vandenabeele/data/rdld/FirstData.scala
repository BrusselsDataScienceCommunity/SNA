package com.vandenabeele.data.rdld

/**
 * Created by peter_v on 01/09/14.
 */

import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf

case class FirstData(val foo: String) {
  val appName = "FirstData"
  val master = "local"
  val conf = new SparkConf().setAppName(appName).setMaster(master)
  val sc = new SparkContext(conf)
  val distFile = sc.textFile("/usr/share/dict/words")
  val c = distFile.count()

  println("count from local filesystem = ")
  println(c)

  val bigWords100M = sc.textFile("hdfs://Peters-MacBook-Pro-2.local:9000/test/big_words_100M")
  println("count from hdfs local for 100M = ")
  println(bigWords100M.count())

  val bigWords200M = sc.textFile("hdfs://Peters-MacBook-Pro-2.local:9000/test/big_words_200M")
  println("count from hdfs local for 200M = ")
  println(bigWords200M.count())

  //val bigWords1G = sc.textFile("hdfs://Peters-MacBook-Pro-2.local:9000/test/big_words_1G")
  //println("count from hdfs local for 1G = " + bigWords1G.count())
}
