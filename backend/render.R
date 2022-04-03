args = commandArgs(trailingOnly=TRUE)
library(rmarkdown)
render("infographics.Rmd", output_file=paste(c(args[1], ".html"), sep="", collapse=""), params = list(csv_file_1 = paste(c(args[1], "_1.csv"), sep="", collapse=""), csv_file_2 = paste(c(args[1], "_2.csv"), sep="", collapse=""), csv_file_3 = paste(c(args[1], "_3.csv"), sep="", collapse="")))
