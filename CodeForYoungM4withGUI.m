%% Original CDS Code Developed by Senior Design team 18071(Courtney Comrie, Patarajarin Akarapipad, Cody Thivener, Ben Weiss, Sean Copeland), Spring 2019 (credit:https://www.mathworks.com/matlabcentral/fileexchange/36816-simple-cell-tracking-contour-for-extensional-flow?focused=5233217&tab=function)
clear
clc
close all;  % Close all figure windows except those created by imtool.
imtool close all;  % Close all figure windows created by imtool.
workspace;  % Make sure the workspace panel is showing.
%user_entry = input('prompt', 's')
prompt = {'Enter Trial Number:','Enter Username:','Enter VDO Name:', 'Enter Minimum Applied Voltage (V):', 'Enter Maximum Applied Voltage (V):'};
dlgtitle = 'Graphic User Interface';
dims = [1 60];
definput = {'1','User1','0-10Vp1.avi','15','90'};
answer = inputdlg(prompt,dlgtitle,dims,definput);
TrialNumber=answer{1};
Username=answer{2};
VDO = answer{3};
voltage_initial = answer{4};
voltage_initial = str2num(voltage_initial);
Voltage_final = answer{5};
Voltage_final = str2num(Voltage_final);

%0-10Vp1.avi
%% Read images from .avi
cellmov = VideoReader(VDO);
Frame_rate = cellmov.FrameRate;
nFrames = cellmov.NumberOfFrames;
vidHeight = cellmov.Height;
vidWidth = cellmov.Width;
fRate = cellmov.FrameRate;
%% analyze each image
MaxLength = [];
MinLength = [];
for j = 1:nFrames
    imageData = read(cellmov,j);
    fr(j).cdata = imageData;
    %imshow(imageData)

    % crop image
    if j == 1
        [J, rect] = imcrop(imageData);
    end
    cropimage = imcrop(imageData, rect); % depend on each VDO
      if j == 1
         firstImage = cropimage;
         %figure()
%          imshow(firstImage)
        
     end   
    %Converts RGB image to grayscale
    grayData = rgb2gray(cropimage);
%     figure()
%     imshow(grayData)
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
%      figure()
%     imshow(I5)    
    %Morphologically open binary image (remove small objects)
    BWoutline = bwperim(I5);
    Segout = cropimage;
    Segout(BWoutline) = 255;
        %Show the outline of the image processing function on the original
        %images while the program is running
    %figure(), imshow(Segout);
    s(j).cdata = Segout;
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
Area(j,:) = graindata.Area;

end

% frames = cat(4,s.cdata); 
% figure, montage({frames,plot(Voltage,MxLenMic),plot(Voltage,MxLenMic)}); %Display multiple image frames as rectangular montage
MxLenMic=pix2micron(MaxLength, 'L')
AreaMic = pix2micron(Area, 'A')
%Voltage = [0,0.5,1,1.5,2,2.5]' % random number for now- change according to actual data
Voltage = linspace(voltage_initial,Voltage_final,length(MxLenMic))

% New cal
ElectricFieldStrength = Voltage/10;
x=ElectricFieldStrength;
% y = (4.9e-14*x.^4) - (1.2e-12*x.^3) + (6.5e-11*x.^2) - (2.4e-11.*x) + (2e-11)
y = (4.9e-14*x.^4) - (1.2e-12*x.^3) + (6.5e-11*x.^2) - (2.4e-11.*x)
Newstress = y ./ (AreaMic' * 10^(-12))

Voltage=Voltage'
figure()
plotExt = plot(Voltage,MxLenMic)
grid on;
xlabel('Voltage');ylabel('Cell Length');
title('Extent of Cell Deformation');

% Stress = Voltage./Area
%disp(Stress);

Strain = (MxLenMic - MxLenMic(1))/MxLenMic(1);
disp(Strain);

% YoungModulus = Stress./Strain;
YoungModulus = Newstress./Strain;

disp(YoungModulus);


figure();
plotYoung = plot(Strain,Newstress,'LineWidth',2);
grid on;
xlabel('Strain');ylabel('Stress');
title('Young''s Modulus');

frames = cat(4,fr.cdata); 
figure, montage(frames); %Display multiple image frames as rectangular montage
figure()
subplot(3,3,1)
imshow(firstImage)
title('Original Image 1', 'FontSize', 10);
for j = 1:6 %6 or nFrames

    subplot(3,3,j+1)
    imshow(s(j).cdata)
    title(['Traced Image ',num2str(j)], 'FontSize', 10);
    if j == 6
%         supplot(3,3,j+1)
%         imshow(firstImage)
         subplot(3,3, j+2)
        plot(Voltage,MxLenMic)
        grid on;
        xlabel('Voltage');ylabel('Cell Length');
        title('Extent of Cell Deformation');
        subplot(3,3, j+3)
        plot(Strain,Newstress,'LineWidth',2);
        grid on;
        xlabel('Strain');ylabel('Stress');
        title('Young''s Modulus');
    end
end
Frame_rate 
% rect

function p2m = pix2micron(pix, type)% type 'L' for length and 'A' for Area
    magnification = 1000;
    mic = 17; % 17 micron diameter of field of view
        pixSizeCal = 2729-58; %  
        ratioMicPix = mic/pixSizeCal; % 1micron: ...Pix
    if type == 'L'
        actualSize = pix*ratioMicPix;
        p2m = actualSize;
    end
    if type == 'A'
        actualSize = pix*ratioMicPix;
        p2m = actualSize;
    end
end
