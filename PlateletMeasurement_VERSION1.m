%% Original CDS Code Developed by Senior Design team 18071(Courtney Comrie, Patarajarin Akarapipad, Cody Thivener, Ben Weiss, Sean Copeland), Spring 2019
clear
clc
close all;  % Close all figure windows except those created by imtool.
imtool close all;  % Close all figure windows created by imtool.
workspace;  % Make sure the workspace panel is showing.

%% Read images from .avi
cellmov = VideoReader('0-10Vp1.avi');  
nFrames = cellmov.NumberOfFrames;
vidHeight = cellmov.Height;
vidWidth = cellmov.Width;
fRate = cellmov.FrameRate;
%% analyze each image
MaxLength = [];
MinLength = [];
for j = 1:nFrames
    imageData = read(cellmov,j);
    % crop image
    cropimage = imcrop(imageData, [150 50 500 400]); % depend on each VDO
    %Converts RGB image to grayscale
    grayData = rgb2gray(cropimage);
    %Automatically computes an appropriate threshold to convert
    level = graythresh(grayData);
    %grayscale image to binary
    bw = im2bw(grayData,level); %ori level,0.25
    bw = bwareaopen(bw,90);
    I3 = imfill(bw,'holes');
    I3 = imclearborder(I3, 4);
    seD = strel('diamond',1);    
    I3 = imerode(I3,seD); 
    I3 = imerode(I3,seD); 
    %Removes background noise
    %Find edges of a binary image (1's and 0's)
    I4 = edge(I3);
    %Fill image regions and holes
    I5 = bwareaopen(I4,80,8);
    %Morphologically open binary image (remove small objects)
    BWoutline = bwperim(I5);
    Segout = cropimage;
    Segout(BWoutline) = 255;
        %Show the outline of the image processing function on the original
        %images while the program is running
    figure(7+j), imshow(Segout);
    cc = bwconncomp(I5,8);
    %Find connected components in a binary image: cc.NumObjects
    if cc.NumObjects > 1 % if there are more than 2 objects, it will get rid of the smaller one
        S = regionprops(cc, 'Area');
        L = labelmatrix(cc);
        P = max(S.Area);
        cc = ismember(L, find([S.Area] >= P));
    end
    %Measures properties of image regions AND SAVES THEM!!!
    graindata = regionprops(cc,'Area','EquivDiameter',...
        'MajorAxisLength','MinorAxisLength','Centroid','Orientation');
    MaxLength(j,:) = graindata.MajorAxisLength;
    MinLength(j,:) = graindata.MinorAxisLength;
%    time(j) = j/fRate; % for plotting graph later
end    
MaxLength;
MinLength;
Voltage = [0,0.5,1,1.5,2,2.5]; % random number for now- change according to actual data
figure()
plot(Voltage,MaxLength)