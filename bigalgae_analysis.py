import os
import bigalgae
import cv2
import numpy
import GPy

def get_algae_window(image_filepath):
    img = cv2.imread(image_filepath, cv2.CV_LOAD_IMAGE_COLOR)
    width, height, channels = img.shape
    thresh_img, contours, hierarchy = bigalgae.threshold_image(img, 21)
    algae_window_img = bigalgae.extract_algae_window(contours, hierarchy, img,
                                                     5.0)
    return(algae_window_img[1])

def return_colour_calibration_dictionary(cropped_algae_window_image):
    thresh_img, contours, hierarchy = bigalgae.threshold_image(
        cropped_algae_window_image, 21)
    corners = bigalgae.get_corner_handles(contours, hierarchy, 5.0)
    corners = bigalgae.sort_corner_handles(corners, contours)
    colours = bigalgae.get_colour_contours_idx(corners, contours)
    colours['black'] = [corner[0] for corner in corners]
    return_dict = {}
    for colour in colours.keys():
        x_vec = []
        y_vec = []
        blue_vec = []
        green_vec = []
        red_vec = []
        for idx in colours[colour]:
            x_ref, y_ref, blue_ref, green_ref, red_ref = (
                bigalgae.return_x_y_rgb(contours[idx],
                cropped_algae_window_image, 6))
            x_vec += x_ref
            y_vec += y_ref
            blue_vec += blue_ref
            green_vec += green_ref
            red_vec += red_ref
        return_dict[colour + '_cal'] = {}
        return_dict[colour + '_cal']['x'] = x_vec
        return_dict[colour + '_cal']['y'] = y_vec
        return_dict[colour + '_cal']['blue'] = blue_vec
        return_dict[colour + '_cal']['green'] = green_vec
        return_dict[colour + '_cal']['red'] = red_vec
    return(return_dict)

def return_central_window_dict(cropped_algae_window_image):
    thresh_img, contours, hierarchy = bigalgae.threshold_image(
        cropped_algae_window_image, 21)
    corners = bigalgae.get_corner_handles(contours, hierarchy, 5.0)
    corners = bigalgae.sort_corner_handles(corners, contours)
    central_window = bigalgae.get_central_window_idx(corners, contours)
    x_ref, y_ref, blue_ref, green_ref, red_ref = bigalgae.return_x_y_rgb(
        contours[central_window], cropped_algae_window_image, 22)
    return_dict = {}
    return_dict['x'] = x_ref
    return_dict['y'] = y_ref
    return_dict['blue'] = blue_ref
    return_dict['green'] = green_ref
    return_dict['red'] = red_ref
    return(return_dict)

def return_prediction(photo, calibration_parameters, max_samples, seed, 
                      wip_image_output_filepath=None):
    sample_strip = get_algae_window(photo)
    if sample_strip == None:
        return(None, None)
    else:
        # Get algae window
        window_dict = return_central_window_dict(sample_strip)
        X_test = numpy.column_stack(
            [window_dict[val] for val in ['x', 'y', 'blue', 'green', 'red']])
        n = int(X_test.shape[0]/max_samples)
        if n == 0:
            n = 1
        rows_to_keep = [i*n for i in range(int(X_test.shape[0]/n))]
        X_test = X_test[rows_to_keep, :]
        # Parameterise the normalization model
        sample_dict = return_colour_calibration_dictionary(sample_strip)
        X = numpy.column_stack(
            [sample_dict['blue_cal'][val] + sample_dict['green_cal'][val] +
            sample_dict['red_cal'][val] + sample_dict['black_cal'][val]
            for val in ['x', 'y', 'blue', 'green', 'red']])
        n = int(X.shape[0]/max_samples)
        if n == 0:
            n = 1
        rows_to_keep = [i*n for i in range(int(X.shape[0]/n))]
        X = X[rows_to_keep, :]
        model_dict = {}
        mean_metalist = []
        sd_metalist = []
        for colour in ['blue', 'green', 'red']:
            y = numpy.hstack(
                    (
                        numpy.random.normal(
                            loc=calibration_parameters['blue_cal'][
                                colour]['mean'],
                            scale=calibration_parameters['blue_cal'][
                                colour]['sd'],
                            size=len(sample_dict['blue_cal']['x'])),
                        numpy.random.normal(
                            loc=calibration_parameters['green_cal'][
                                colour]['mean'],
                            scale=calibration_parameters['green_cal'][
                                colour]['sd'],
                            size=len(sample_dict['green_cal']['x'])),                           
                        numpy.random.normal(
                            loc=calibration_parameters['red_cal'][
                                colour]['mean'],
                            scale=calibration_parameters['red_cal'][
                                colour]['sd'],
                            size=len(sample_dict['red_cal']['x'])),                           
                        numpy.random.normal(
                            loc=calibration_parameters['black_cal'][
                                colour]['mean'],
                            scale=calibration_parameters['black_cal'][
                                colour]['sd'],
                            size=len(sample_dict['black_cal']['x']))
                    )
                )
            y = y[rows_to_keep, None]
            kern_rbf = GPy.kern.RBF(5, ARD=True)
            kern_linear = GPy.kern.Linear(5, ARD=True)
            kern = kern_rbf + kern_linear
            model = GPy.models.GPRegression(X, y, kern)
            model.optimize()
            model_dict[colour] = model
            gpy_mean, gpy_var = model.predict(X_test)
            mean_metalist.append(gpy_mean)
            sd_metalist.append(numpy.sqrt(gpy_var))
        return_dict = {'mean': numpy.column_stack(mean_metalist), 
                    'sd': numpy.column_stack(sd_metalist)}
        if not wip_image_output_filepath is None:
            del(X, y)
            size = 150
            resized_img = cv2.resize(sample_strip, (size, size))
            blue_vec, green_vec, red_vec = [list(matrix.flatten())
                for matrix in cv2.split(resized_img)]
            y_vec = [y for y in range(size) for x in range(size)]
            x_vec = range(size) * (size)
            stack = numpy.column_stack((x_vec, y_vec, blue_vec, green_vec,
                                        red_vec))
            del(x_vec, y_vec, blue_vec, green_vec, red_vec)
            predicted_img_mean = []
            for colour in ['blue', 'green', 'red']:
                predicted_img_mean.append(model_dict[colour].predict(stack)[0])
            predicted_img_mean = numpy.column_stack(predicted_img_mean)
            gpy_img = cv2.merge((predicted_img_mean[:,0].reshape((size, size)),
                                predicted_img_mean[:,1].reshape((size, size)),
                                predicted_img_mean[:,2].reshape((size, size))))
            file_name, extension = photo.split('/')[-1].split('.')
            original_output_filepath = (wip_image_output_filepath +
                '/' + file_name + '_original.' + extension)
            normalized_output_filepath = (wip_image_output_filepath +
                '/' + file_name + '_gpy.' + extension)
            cv2.imwrite(original_output_filepath, resized_img)
            cv2.imwrite(normalized_output_filepath, gpy_img)
        return(return_dict, X_test)
