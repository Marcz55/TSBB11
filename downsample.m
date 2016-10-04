%%%
% This script downsamples images taken to the size 224 x 224 to fit
% to the neural network used.
%%%

% Asks for where the images is stored and if the camera used is a
% Narrative camera or not
% Don't enter only a Return key to the program, it will throw the error
% "Index exceed matrix dimension"
promt = 'Please input the path to the files: \n';
path_to_folder = input(promt,'s');
while isempty(path_to_folder)
    path_to_folder('wrong format, please enter a new path');
end

promt = 'Is the camera a narrative camera? input Y/N: \n';
answer = input(promt,'s');
while (not(strcmp(answer , 'Y')) && not(strcmp (answer,'N')))
    answer = input(promt , 's');
end
promt = 'Please give the path to where to save the image(s):\n';
path_save = input(promt,'s');
while isempty(path_to_folder)
    path_save('save path is empty, please enter a new path');
end
outputsize = 224;

% Loops thorugh the provided folder

files = dir(path_to_folder);
for k = 1:length(files)
    [pathstr, name, ext] = fileparts(files(k).name);
    if strcmp(ext,'.jpg') || strcmp(ext,'.JPG');
        file_path = strcat(path_to_folder,'/',name,ext);
        % Load images
        original = imread(file_path);
        switch (answer)
            case 'Y' % Narrative camera
                downsampled = imresize(original,[224 NaN]);
                
            case 'N' % Not a narrative camera
                for rowsize = 224:300
                    downsampled = imresize(original, [rowsize NaN]);
                    colsize = size(downsampled,2);
                    while colsize < 224
                        downsampled = imresize(original, [rowsize NaN]);
                    end
                    break
                end       
        end
        % takes out the correct dimension
        col = size(downsampled,2);
        diffX = abs(outputsize - col);
        minX = floor(diffX/2)+1;
        maxX = col-ceil(diffX/2);
        minY = 1;
        maxY = size(downsampled,1);
        
        correct_size = downsampled(minY:maxY,minX:maxX,:);
        
        % Save the croped image to the specific folder given
        path_name = strcat(path_save,'/',name,ext);
        imwrite(correct_size,path_name)
    end
end
