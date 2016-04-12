import os
import bigalgae_analysis
import numpy

#Collect all the image filepaths
training_images_filepath = 'training_images'
uploaded_images_filepath = 'uploaded_images'
photos = (['/'.join([training_images_filepath, run_folder, file_name]) for
    run_folder in os.listdir(training_images_filepath) for file_name in
    os.listdir('/'.join([training_images_filepath, run_folder]))] +
    ['/'.join([uploaded_images_filepath, file_name]) for file_name in
    os.listdir(uploaded_images_filepath)])
#Import the reference calibration strip
reference = './reference.jpg'
calibration_strip = bigalgae_analysis.get_algae_window(reference)
calibration_dictionary = (
    bigalgae_analysis.return_colour_calibration_dictionary(calibration_strip))
calibration_parameters = {
    i: {
        j: {
            'mean': numpy.mean(calibration_dictionary[i][j]),
            'sd': numpy.std(calibration_dictionary[i][j])
        } for j in ['blue', 'red', 'green']
    } for i in ['blue_cal', 'red_cal', 'green_cal', 'black_cal']
}
del(calibration_dictionary)
buffer_string = '\t'.join(['file_name', 'points_sampled', 'blue_mean',
    'blue_sd', 'green_mean', 'green_sd', 'red_mean', 'red_sd',
    'blue_mean_prenorm', 'blue_sd_prenorm', 'green_mean_prenorm',
    'green_sd_prenorm', 'red_mean_prenorm', 'red_sd_prenorm']) + '\n'
for points_to_sample in [100, 500]:
    for photo in photos:
        wip_image_filepath = 'temp/wip_images'
        if len(photo.split('/')) == 3:
            wip_image_filepath += '/' + photo.split('/')[1]
        if not os.path.exists(wip_image_filepath):
            os.mkdir(wip_image_filepath)
        print(photo)
        predict, pre_normalized = bigalgae_analysis.return_prediction(
            photo, calibration_parameters, points_to_sample, 42,
            wip_image_filepath)
        if predict == None:
            buffer_string += '\t'.join([photo, str(points_to_sample)] +
                ['NA'] * 12) + '\n'
        else:
            sample_strip = bigalgae_analysis.get_algae_window(photo)
            window_dict = bigalgae_analysis.return_central_window_dict(
                sample_strip)
            sampled_blue_values = [
                numpy.random.normal(loc=predict['mean'][i,0],
                                    scale=predict['sd'][i,0]) for i in range(
                                        predict['mean'].shape[0])]
            sampled_green_values = [
                numpy.random.normal(loc=predict['mean'][i,1],
                                    scale=predict['sd'][i,1]) for i in range(
                                        predict['mean'].shape[0])]
            sampled_red_values = [
                numpy.random.normal(loc=predict['mean'][i,2],
                                    scale=predict['sd'][i,2]) for i in range(
                                        predict['mean'].shape[0])]
            buffer_string += '\t'.join([str(val) for val in [
                photo,
                str(points_to_sample),
                numpy.mean(sampled_blue_values),
                numpy.std(sampled_blue_values),
                numpy.mean(sampled_green_values),
                numpy.std(sampled_green_values),
                numpy.mean(sampled_red_values),
                numpy.std(sampled_red_values),
                numpy.mean(pre_normalized[:,2]),
                numpy.std(pre_normalized[:,2]),
                numpy.mean(pre_normalized[:,3]),
                numpy.std(pre_normalized[:,3]),
                numpy.mean(pre_normalized[:,4]),
                numpy.std(pre_normalized[:,4])]]) + '\n'
with open('temp/analysis_output.tsv', 'w') as f:
    f.write(buffer_string)
