rm(list=ls(all=TRUE))
library(tidyr)
library(ggplot2)
library(scales)

training_data <- read.table('training_data.tsv', header=TRUE, sep='\t',
    stringsAsFactors=FALSE)
training_data$file_name <- paste0('training_images/run_', training_data$run, '/', training_data$file_name)
uploaded_data <- read.table('uploaded_data.tsv', header=TRUE, sep='\t',
    stringsAsFactors=FALSE)
uploaded_data$file_name <- paste0('uploaded_images/', uploaded_data$file_name)
picture_information <- read.table('temp/analysis_output.tsv', header=TRUE,
    sep='\t',  stringsAsFactors=FALSE)
picture_information_500 <- picture_information[
    picture_information$points_sampled==500,]

training_data <- cbind(training_data, picture_information_500[
    match(training_data$file_name, picture_information_500$file_name),])
training_data$od_680_mean <- apply(training_data[,
    grepl('od_680', names(training_data))], 1, mean, na.rm=TRUE)
training_data$od_750_mean <- apply(training_data[,
    grepl('od_750', names(training_data))], 1, mean, na.rm=TRUE)

measures <- c('cell_concentration_g_per_l', 'cells_per_ml', 'od_680_mean',
    'od_750_mean')
training_data_long <- training_data[,c(1:5, 17:22,
    which(names(training_data) %in% measures))]
training_data_long <- gather(training_data_long, colour, colour_value,
    -(file_name:day), -one_of(measures))
training_data_long <- separate(training_data_long, colour,
    into=c('colour', 'type'), sep='_')
training_data_long <- spread(training_data_long, type, colour_value)
colnames(training_data_long)[match(measures, colnames(training_data_long))] <-
    c('Cell Concentration (g/l)', 'Cell Density (cells / ml)', 'OD 680nm',
    'OD 750nm')
training_data_long <- gather(training_data_long, measurement_type, measurement,
    -(file_name:day), -(colour:sd))
training_data_long$colour <- c('Blue', 'Green', 'Red')[
    match(training_data_long$colour, c('blue', 'green', 'red'))]

p <- ggplot(training_data_long, aes(x=measurement, y=mean, col=colour))
p <- p + geom_point()
p <- p + geom_errorbar(aes(ymax=mean+sd, ymin=mean-sd))
p <- p + facet_grid(colour ~ measurement_type, scales='free_x')
p <- p + labs(x = '', y='Colour Intensity')
p <- p + scale_colour_manual(values=rev(hue_pal()(3)))
p <- p + theme(legend.position='none')
png('figures/training.png', height=480, width=960, res=100)
print(p)
dev.off()

picture_information_long <- gather(picture_information, colour, colour_value, -(file_name:points_sampled))
picture_information_long <- separate(picture_information_long, colour,
    into=c('colour', 'type', 'prenorm'), sep='_')
picture_information_long <- unite(picture_information_long, type, type, prenorm)
picture_information_long <- spread(picture_information_long, type, colour_value)
picture_information_long$colour <- c('Blue', 'Green', 'Red')[
    match(picture_information_long$colour, c('blue', 'green', 'red'))]

p <- ggplot(picture_information_long, aes(x=mean_prenorm, y=mean_NA, col=colour))
p <- p + geom_point()
p <- p + geom_errorbar(aes(ymax=mean_NA+sd_NA, ymin=mean_NA-sd_NA))
p <- p + geom_errorbarh(aes(xmax=mean_prenorm+sd_prenorm, xmin=mean_prenorm-sd_prenorm))
p <- p + facet_grid(points_sampled ~ colour, scales='free_x')
p <- p + scale_colour_manual(values=rev(hue_pal()(3)))
p <- p + theme(legend.position='none')
png('figures/prenorm_vs_norm.png', height=480, width=960, res=100)
print(p)
dev.off()

picture_information_long <- gather(picture_information, colour, colour_value, -(file_name:points_sampled))
picture_information_long <- separate(picture_information_long, colour,
    into=c('colour', 'type', 'prenorm'), sep='_')
picture_information_long <- picture_information_long[
    picture_information_long$type=='mean',]
picture_information_long <- picture_information_long[
    picture_information_long$file_name %in% uploaded_data$file_name,]
picture_information_long$file_name <- paste('Experiment:',
    uploaded_data$experiment, 'Date:', uploaded_data$date_uploaded)[
    match(picture_information_long$file_name, uploaded_data$file_name)]
picture_information_long <- unite(picture_information_long, type, colour, prenorm)
picture_information_long$type <- gsub('_NA', '\nPost', picture_information_long$type)
picture_information_long$type <- gsub('_prenorm', '\nPre', picture_information_long$type)
picture_information_long$type <- paste0(
    toupper(substr(picture_information_long$type, 1, 1)),
    substr(picture_information_long$type, 2,
    nchar(picture_information_long$type)))
picture_information_long$col <- substr(picture_information_long$type, 1, 1)

p <- ggplot(picture_information_long, aes(factor(type), colour_value,
    fill=col))
p <- p + geom_boxplot()
p <- p + facet_grid(points_sampled ~ file_name, scales="free", space="free")
p <- p + scale_fill_manual(values=rev(hue_pal()(3)))
p <- p + theme(legend.position='none')
p <- p + labs(x = '', y='Colour Intensity')
png('figures/boxplot.png', height=480, width=960, res=100)
print(p)
dev.off()
