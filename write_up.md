1) Website
The data which is collected when an image is uploaded and the checks the images are put through to verify that they are valid images of the calibration strip.

2) Algorithm - Details of the Gaussian Process based normalization algorithm. I'll include figures of the data James' student collected as well as figures showing how effective the normalization algorithm is. I can't comment here on determining the algal density from images as we'd need more training data for that.

3) Challenges and Outlook - The problems faced with the normalization algorithm and and how we overcame / could overcome them in the future.

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


2 - Algorithm
=============

The image analysis pipeline has been developed in Python using the OpenCV computer vision library [1] and consists of calibration window detection and image normalization.

Detection of the calibration window
-----------------------------------

TODO - Add visual description of method
Images are converted to greyscale and have a Gaussian blur applied to them before they are subjected to a threshold.
The threshold converts images into black and white images, to which a contour finding algorithm is applied.
Contours are arranged into a tree like structure, with a contour's parent being the contour which contains it.
In order to find the three anchor points of the calibration window the algorithm iterates over the list of contours and finds contours whose areas are in the correct ratios.
The ratios which the algorithm looks for are a 9:16 area ratio between a contour and its parent and a 9:25 area ratio between a contour and its grandparent.
Once three anchor points are found, the image is transformed to orient the picture correctly and correct any skewing of the image.

Image normalization
-------------------

TODO - Add box plots
TODO - Add comparison photographs
Using the positions of the anchor points, the coloured squares and the transparent window are located in the image and the pixel information for them extracted.
The pixel information consists of red, green and blue channel values, which take integer values between 0 and 255 inclusive and well as positional information.
To allow the algorithm to run in reasonable time, the number of pixels may be downsampled.
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
The output from the Gaussian process models are mean and variance values for each colour channel (Figure 1).


3 - Challenges and Outlook
==========================

Website plotting features using D3
----------------------------------

To facilitate the use of the website to track algal growth over time, options to graph the data will be implemented.
These graphing options will make use of D3, a JavaScript visualization library.
The advantage of client side visualization is reduced server side computation as well as responsive, dynamic plots.
The plot will allow the user to plot different measures of algal density (260/280 ratio, dry mass and cell count) against time.
The time measurement will be determined in three ways, with the order of presidence determined by their differing levels of accuracy.
The most accurate method of time elapsed since the start of the experiment is the Arduino based time.
If the image analysis pipeline does not detect a time window in the photo, and EXIF data is available, the date and time the photo was taken is taken from the photo's metadata.
The disadvantage of using the metadata is that the internal date and time set on the phone may be incorrect or set to a different time zone.
The final time used is the time the image was uploaded to the server.
The disadvantage of using this time is that users may take photos are upload them at a later time.
This may be the case if Internet access is intermittant or is not possible on the device the user is using, such as when a digital camera is used to capture the images.

Normalization algorithm - pixel sampling
----------------------------------------

TODO - Add number of sampled points comparisons
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

Prediction of algal density
---------------------------

Currently the image analysis pipeline just checks for the presence or absence of the calibration window when an image is uploaded.
Once more training data has been obtained, however, the image will be normalized, a prediction of the algal density within the bioreactor will be made and the result will be sent to the user within a few seconds.
While currently unvalidated by experimental data, the method of algal density prediction carried out by the image analysis pipeline will consist of a GP regression model.
In order to relate the colour of the algal reaction mixture to algal density, the distribution of values for each colour channel needs to be known.
For each pixel normalized using the Gaussian process method detailed above, a normalized mean value and a variance value are given as output for each colour channel.
Finding the algal reaction mixture colour values for each channel by averaging the normalized pixel mean colour values would not incorporate the variation observed for each pixel.
Therefore, to incorporate the variation, the per pixel probability distributions are combined and points are sampled from the combined probability distribution.
An overall mean and variance for the algal reaction mixture for each colour channel are then calculated from the sampled values.
The colour values for the algal reaction mixture are used as inputs to another Gaussian process model to allow for prediction of the algal density measurements (Figure 2).


References
==========
1. Bradski, G., OpenCV Library, Dr. Dobb's Journal of Software Tools, 2000.
2. The GPy authors, [GPy](http://github.com/SheffieldML/GPy): A Gaussian process framework in Python, 2012-2015.
