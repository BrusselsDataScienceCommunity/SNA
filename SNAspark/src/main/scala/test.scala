
import org.apache.spark.sql
import org.apache.spark.sql._
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf

object test1 {
  def main(args: Array[String]) {
    val fileName = "/Users/tcarette/Documents/Projets-Divers/data4good_and_co/handsOnGraph/data/profilesFromKeywords.json" // Should be srme file on your system

//  Spark context
    val conf = new SparkConf().setAppName("Test 1")
    val sc = new SparkContext(conf)

//    simple text analysis
    val rawData = sc.textFile(fileName, 2).cache()
    val numAs = rawData.filter(line => line.contains("a")).count()
    val numBs = rawData.filter(line => line.contains("b")).count()
    println("Lines with a: %s, Lines with b: %s".format(numAs, numBs))

//  SQL context
//    val sqlc = new org.apache.spark.sql.SQLContext(sc)
//    import sqlc.createSchemaRDD

//  Schema
//    val profiles = sqlc.jsonFile(fileName)
//    profiles.printSchema()

  }
}
