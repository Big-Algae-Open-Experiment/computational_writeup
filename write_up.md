The computational methods developed as part of the Big Algae Open Experiment consist of the website associated with the project and the image analysis pipeline.
An explanation of the methods and some preliminary results from them are provided, along with some challenges faced during the project and an outlook for the directions the project could take in the future.


1 - Website
===========

To allow for data collection and information dissemination, a centralized online platform was created (http://bigalgae.com).
Through this platform, general information about the Big Algae Open Experiment was made available and users can register bioreactors.
Registration requires a team name, an e-mail address and the location of the bioreactor.
Location information is collected to allow the environmental conditions experienced by bioreactors placed outdoors to be determined.
After validating a user's email address upload and experiment validation codes are sent to the user.
These codes are required to upload data and register new experiments for a particular reactor respectively.
Having a form of validation such as this lowers the risk of abuse significantly, without negatively affecting the usability of the site.
When uploading an image cell count data and optical density measurements may also be uploaded, with dry mass information being uploaded retropectively.
During the image upload process, the image enters the image analysis pipeline to determine whether it contains a calibration window and an Arduino controlled time display (Section 2 - Algorithm).
Presence of the calibration window is essential for the upload to be successful, while the presence of the time display is not.
The online platform was created using a Python web framework called Flask, hosted using DigitalOcean cloud infrastructure and made use of Ansible to automate server management tasks.
The Google Maps and Google Places application programming interfaces were utilized to provide interactive maps on the site and to determine longitude and latitude information for each bioreactor.


2 - Image analysis pipeline
===========================

The image analysis pipeline has been developed in Python using the OpenCV computer vision library [1] and consists of calibration window detection and image normalization.

Detection of the calibration window
-----------------------------------

Images are converted to greyscale and have a Gaussian blur applied to them before they are subjected to a threshold.
The threshold converts images into black and white images, to which a contour finding algorithm is applied.
Contours are arranged into a tree like structure, with a contour's parent being the contour which contains it.
In order to find the three anchor points of the calibration window the algorithm iterates over the list of contours and finds contours whose areas are in the correct ratios.
The ratios which the algorithm looks for are a 9:16 area ratio between a contour and its parent and a 9:25 area ratio between a contour and its grandparent.
Once three anchor points are found, the image is transformed to orient the picture correctly and correct any skewing of the image.

Image normalization
-------------------

Using the positions of the anchor points, the coloured squares and the transparent window are located in the image and the pixel information for them extracted.
The pixel information consists of red, green and blue channel values, which take integer values between 0 and 255 inclusive and well as positional information.
To allow the algorithm to run in reasonable time, the number of pixels is downsampled.
To normalize the colours, a Gaussian process model is applied to each colour channel (red, green and blue) separately.
Gaussian processes are a probabilistic framework used to model unknown functions, and are used in this study because of the unknown non-linearities involved when normalizing photos taken using different equipment and lighting conditions.
They are implemented in the algorithm using the GPy Python library [2].
To parameterize the Gaussian process models, pixel information from the coloured squares and from the black squares within the anchor points are used.
Positional as well as RGB values of the pixels are combined to ensure that variation due to the camera and lighting can be taken into account.
The Gaussian process models are constructed using a linear kernel combined with a squared exponential kernel.
This allows the model to capture the general linear trend while also allowing for non-linearities to be considered by the model.
The pixel information from an image as well as from a reference image of the calibration window are used to train the models for each colour channel.
Once parameterized, the Gaussian process models are used to normalize the pixel information from the transparent section of the calibration window, which corresponds to the colour of the algae in the bioreactor.
Each pixel is normalized by inputting its position in the image as well as its unnormalized RGB values into each Gaussian process model.
The output from the Gaussian process models are mean and variance values for each colour channel.

![Figure 1](https://github.com/Big-Algae-Open-Experiment/computational_writeup/blob/master/figures/comparison.png)

Figure 1 demonstrates the effect the normalization algorithm has on a selection of six images.
The pixels from the coloured squares in the reference image (Figure 1a) are used to train a Gaussian process model for each colour channel within each image.
Figures 1b-1g are the unnormalized images uploaded to the site after they have undergone image transformation to orient the anchor points.
Figures 1h-1m are the corresponding normalized images after the Gaussian process based algorithm has been applied.

![Figure 2](https://github.com/Big-Algae-Open-Experiment/computational_writeup/blob/master/figures/prenorm_vs_norm.png)

Figure 2 shows the relationship between colour intensity values before and after the normalization algorithm has been applied for each colour channel separately.
The two rows of the figure correspond to the results of the normalization algorithm when sampling 100 pixels from the images and when sampling 500 pixels from the images.
The relationships between the pre- and post-normalization values all show non-linearities, validating the application of Gaussian processes to this colour normalization problem.
Also striking is the similarities between running the algorithm using 100 pixels to train the Gaussian processes and sample and using 500 pixels.
This result implies that downsampling the image to as low as 100 pixels is still capable of capturing the variability in the pixel colour intensities.

![Figure 3](https://github.com/Big-Algae-Open-Experiment/computational_writeup/blob/master/figures/boxplot.png)

Figure 3 demonstrates the effect of the normalization algorithm on the mean measurements of colour intensity for repeated measurements.
Two bioreactors were setup and photographed on two separate dates.
Assuming the algal density did not change significantly throughout the time the bioreactors were photographed, the images taken can be seen as repeated measurements.
For each repeat measurement, the mean colour intensity for the algal window was calculated before and after the normalization algorithm was applied.
The spread of these mean values after the normalization algorithm was applied increased in some cases, such as the blue and green channels in the 'Experiment: 2 Date: 2016-02-13' sample.
This trend was not consistent however, with a decrease in the interquartile range observed in all colour channels post-normalization in the 'Experiment 2: Date: 2016-02-20' sample.


3 - Challenges and Outlook
==========================

Website plotting features using D3
----------------------------------

To facilitate the use of the website to track algal growth over time, options to graph the data will be implemented.
These graphing options will make use of D3, a JavaScript visualization library.
The advantage of client side visualization is reduced server side computation as well as responsive, dynamic plots.
The plot will allow the user to plot different measures of algal density (optical density measurements, dry mass and cell count) against time.
The time measurement will be determined in three ways, with the order of presidence determined by their differing levels of accuracy.
The most accurate method of time elapsed since the start of the experiment is the Arduino based time.
If the image analysis pipeline does not detect a time window in the photo, and EXIF data is available, the date and time the photo was taken is taken from the photo's metadata.
The disadvantage of using the metadata is that the internal date and time set on the phone may be incorrect or set to a different time zone.
The final time used is the time the image was uploaded to the server.
The disadvantage of using this time is that users may take photos are upload them at a later time.
This may be the case if Internet access is intermittant or is not possible on the device the user is using, such as when a digital camera is used to capture the images.

Pixel sampling in the normalization algorithm
---------------------------------------------

The Gaussian process image normalization process requires many matrix computations to be carried out.
The size of the matricies being used in the computations is directly related to both the number of colour square pixels being used to train the Gaussian process and the number of pixels sampled from the algal window.
Although a more accurate estimation of the RGB colour value of the algal window would be obtained by using more pixels to train the GP model and by sampling more pixels from the algal window, this has to be balanced with the computational run time of the image analysis pipeline.
The computational run time of the image analysis pipeline is pivotal to the final user experience of the website.
If the computational run time is exceeds when the user uploads an image, the website may feel unresponsive.
Conversely, if the image analysis pipeline was run in a batch manner, the data points from uploaded images would only become visible on the growth graph when the pipeline is run.
This would have the effect of reducing the gratification the user receives from contributing to the project.
To counter these problems, a two pass image analysis pipeline could be implemented.
The first pass of the pipeline would be executed when the image was uploaded, and would the number of pixels sampled during this pass would be low to reduce the computational run time.
The pipeline could then execute the second pass during times when the website is less active.
The second pass would consist of the image alaysis algorithm being run using more pixels in the training and prediction steps than the first pass.
Because a user does not wait for the response of the second pass, the computational run time of the second pass does not impact the user experience of the website.
Reassuringly, using 100 sampled pixels does not result in a marked difference in the final results obtained using 500 sampled pixels (Figure 2 and 3).
Despite this observation, the use of more sampled pixels does allow the variation present in each image to be better estimated and reduces the interquartile range observed between repeated measurements post-normalization (Figure 3).
The improvement in the estimations validates the use of a two pass image analysis approach in the future.

Prediction of algal density
---------------------------

Currently the image analysis pipeline just checks for the presence or absence of the calibration window when an image is uploaded, and does not estimate algal density measures.
During the project, a number of algal growth experiments were carried out to record algal growth using accurate quantification measures.
The measures used were cell concentration (g / l), cell density (cells / ml) and optical density measurements carried out at wavelengths of 680nm and 750nm.
Also recorded were images of the bioreactor with a calibration strip fitted.

![Figure 4](https://github.com/Big-Algae-Open-Experiment/computational_writeup/blob/master/figures/training.png)

The relationship between the accurate quantification measures and the colour intensities as predicted by the normalization algorithm show non linear trends in all cases.
The trends seem to follow inverse relationships, whereby the lower the colour intenity the higher the measure of algal density.
This makes intuitive sense given that as the algal reaction mixtures becomes denser less of the white background is observed.
This trend also suggests that estimating algal density using digital images of the reaction mixture will be most sensitive within a certain range of density values.
Currently, the number of data points collected is not sufficient to form training and testing datasets to validate any prediction algorithm.
Once more training data has been obtained, however, the image will be normalized, a prediction of the algal density within the bioreactor will be made and the result will be sent to the user within a few seconds.
While currently unvalidated by experimental data, the method of algal density prediction carried out by the image analysis pipeline will consist of a GP regression model.
In order to relate the colour of the algal reaction mixture to algal density, the distribution of values for each colour channel needs to be known.
For each pixel normalized using the Gaussian process method detailed above, a normalized mean value and a variance value are given as output for each colour channel.
Finding the algal reaction mixture colour values for each channel by averaging the normalized pixel mean colour values would not incorporate the variation observed for each pixel.
Therefore, to incorporate the variation, the per pixel probability distributions are combined and points are sampled from the combined probability distribution.
An overall mean and variance for the algal reaction mixture for each colour channel are then calculated from the sampled values.
The colour values for the algal reaction mixture are used as inputs to another Gaussian process model to allow for prediction of the algal density measurements (Figure 4).


References
==========
1. Bradski, G., OpenCV Library, Dr. Dobb's Journal of Software Tools, 2000.
2. The GPy authors, [GPy](http://github.com/SheffieldML/GPy): A Gaussian process framework in Python, 2012-2015.
