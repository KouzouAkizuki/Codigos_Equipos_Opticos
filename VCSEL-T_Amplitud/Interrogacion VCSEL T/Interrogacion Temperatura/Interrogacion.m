%% Importacion de los archivos
clc;
clear;

%Constantes
Splitter_40_Atenuacion=-10*log10(48.11/147.2);
Splitter_60_Atenuacion=-10*log10(74/147.2);
Fibra_Optica=0.10055711;
Circulador_1P2=0.399442890076300;
Circulador_2P3=0.429442890076299;

Data_Length=length(table2array(VCSEL_T_Import('VCSEL_T_SSFBG_Amplitud_S1R_16000.0samples_Temp_562_Frequency_16_Iterations_41_Temp_Mount_20.csv')));
TemperatureLength=length(20:1:60);
%Interrogacion a 20°C
Interrogacion_VCSEL=zeros(Data_Length,6,TemperatureLength); %#1 ->Muestras, #2 -> SSFBG, #3 -> REF, #4 -> Trigger, #5 -> Temperatura, #6 -> Tiempo

for i=1:TemperatureLength
    Interrogacion_VCSEL(:,:,i)=table2array(VCSEL_T_Import('VCSEL_T_SSFBG_Amplitud_S1R_16000.0samples_Temp_562_Frequency_16_Iterations_41_Temp_Mount_'+string(i+19)+'.csv'));
end

Trigger_Up=zeros(41,TemperatureLength);
Diff_Index_Prom=zeros(1,TemperatureLength);
for i=1:TemperatureLength
    Trigger_Up(:,i)=find(diff(Interrogacion_VCSEL(:,4,i))>2,41);
    Diff_Index_Prom(:,i)=round(mean(diff( Trigger_Up(:,i))),0);
end


Interrogacion_VCSEL_Mean=zeros(Diff_Index_Prom(1),9,TemperatureLength); %#1 ->Muestras, #2 -> SSFBG, #3 -> REF, #4 -> Trigger, #5 -> Temperatura, #6 -> Tiempo
Interrogacion_VCSEL_std=zeros(Diff_Index_Prom(1),6,TemperatureLength); %#1 ->Muestras, #2 -> SSFBG, #3 -> REF, #4 -> Trigger, #5 -> Temperatura, #6 -> Tiempo

for i=1:TemperatureLength
    for c=((1:Diff_Index_Prom(1))-1)
        for d=((1:40)-1)
            if(d==0)
                Comodin=Interrogacion_VCSEL(Trigger_Up(1,i)+d*Diff_Index_Prom(1)+c,:,i);
            else
                Comodin=vertcat(Comodin,Interrogacion_VCSEL(Trigger_Up(1,i)+d*Diff_Index_Prom(1)+c,:,i));
            end
        end
        Interrogacion_VCSEL_Mean(c+1,1:6,i)=mean(Comodin);
        Interrogacion_VCSEL_std(c+1,:,i)=std(Comodin);
    end
end

%lambda=-1.175692512846067*10^(-5)*V^3-0.027479643004984*v^2+0.043730257712403*v+1549.473640641302

for i=1:TemperatureLength
    Interrogacion_VCSEL_Mean(:,7,i)=((1:Diff_Index_Prom(1))-1)/length(((1:Diff_Index_Prom(1))-1))*-18;
    Interrogacion_VCSEL_Mean(:,8,i)=-1.175692512846067*10^(-5)*(Interrogacion_VCSEL_Mean(:,7,i)).^3-0.027479643004984*(Interrogacion_VCSEL_Mean(:,7,i)).^2+0.043730257712403*(Interrogacion_VCSEL_Mean(:,7,i))+1549.473640641302;
end

Interrogacion_VCSEL_Mean(:,2,:)=0.0627077404*Interrogacion_VCSEL_Mean(:,2,:)-0.0017714024402;
Interrogacion_VCSEL_Mean(:,3,:)=0.06157678362*Interrogacion_VCSEL_Mean(:,3,:)+0.007068472567;
 
Interrogacion_VCSEL_Mean(:,3,:)=Interrogacion_VCSEL_Mean(:,3,:)*10^(Splitter_40_Atenuacion/10)*10^(Fibra_Optica/10)*10^-(Splitter_60_Atenuacion/10)*10^-(Circulador_1P2/10)*10^-(Fibra_Optica/10);
Interrogacion_VCSEL_Mean(:,2,:)=Interrogacion_VCSEL_Mean(:,2,:)*10^(Fibra_Optica/10)*10^(Circulador_2P3/10)*10^(Fibra_Optica/10);

Interrogacion_VCSEL_Mean(:,9,:)=Interrogacion_VCSEL_Mean(:,2,:)./Interrogacion_VCSEL_Mean(:,3,:);

diff=200;

%% Creacion del codigo para el sensor SSFBG SA1R y Barrido de correlacion para determinar lambda central de las temperaturas

N=8; 
Ma=[1 1 0 0 1 0 0 0];  
FWHM_Codes= 0.03467501;                                                                     
dl=         0.097;                                                                       
Offset=0;                                                                 
Orden=1;

Lamda_Central=zeros(TemperatureLength,1);
XCP_ratio=zeros(TemperatureLength,2);
Ideal_Codes=zeros(diff*2+1,TemperatureLength);
TempArray=20:1:60;

minimun=zeros(TemperatureLength,1);
maximun=zeros(TemperatureLength,1);

for c=1:TemperatureLength
    [~,minimun(c)]=maxk(Interrogacion_VCSEL_Mean(:,9,c),1);
    maximun(c)=minimun(c)+diff;
    minimun(c)=minimun(c)-diff;

    [Lamda_Central(c),XCP_ratio(c,:),Ideal_Codes(:,c)]=Correlacion_Ideal(Interrogacion_VCSEL_Mean(:,9,c),Interrogacion_VCSEL_Mean(:,8,c),minimun(c),maximun(c),Offset,FWHM_Codes,N,dl,Ma,Orden);
end          

%Lamda_Central=-1.175692512846067*10^(-5)*(Lamda_Central).^3-0.027479643004984*(Lamda_Central).^2+0.043730257712403*(Lamda_Central)+1549.473640641302;          

Mean_XPC=mean(XCP_ratio(6:end,2));
STD_XPC=std(XCP_ratio(6:end,2));

%% Graficas


Heigth=1080;
Aspect_ratio=2.76;

f1=figure('name','Prueba Preliminar');
plot(Interrogacion_VCSEL_Mean(:,8,1),Interrogacion_VCSEL_Mean(:,9,1),'LineWidth',4,'Color','#00009B');
hold on
grid on
xlabel('Longitud de onda [nm]')
ylabel('Reflectividad [u.a]')
title('Interrogación del sensor SSFBG SA1R a 20°C')
grid on
xlim([min(sort(Interrogacion_VCSEL_Mean(:,8,1))) max(Interrogacion_VCSEL_Mean(:,8,1))])
set(f1,'position',[50,50,Heigth*Aspect_ratio,Heigth])
fontsize(f1, scale=4)  

set(gca, 'units', 'normalized'); %Just making sure it's normalized
Tight = get(gca, 'TightInset');  %Gives you the bording spacing between plot box and any axis labels
                                 %[Left Bottom Right Top] spacing
NewPos = [Tight(1) Tight(2) 1-Tight(1)-Tight(3) 1-Tight(2)-Tight(4)]; %New plot position [X Y W H]
set(gca, 'Position', NewPos);

ax = gca;
ax.LineWidth = 4;
ax.GridLineWidth = 3;


f2=figure('name','Prueba a diferentes temperaturas');
plot(Interrogacion_VCSEL_Mean(:,8,1),Interrogacion_VCSEL_Mean(:,9,1),'LineWidth',4,'Color','#00009B','LineStyle','--');
hold on
plot(Interrogacion_VCSEL_Mean(:,8,20),Interrogacion_VCSEL_Mean(:,9,20),'LineWidth',4,'Color','#9B111E','LineStyle','--');
plot(Interrogacion_VCSEL_Mean(:,8,TemperatureLength),Interrogacion_VCSEL_Mean(:,9,TemperatureLength),'LineWidth',4,'Color','#287233','LineStyle','--');
grid on
xlabel('Longitud de onda [nm]')
ylabel('Reflectividad [u.a]')
title('Interrogación del sensor SSFBG SA1R a diferentes temperaturas')
legend('20°C', '39°C', '60°C')
grid on
xlim([1546 1548])
set(f2,'position',[50,50,Heigth*Aspect_ratio,Heigth])
fontsize(f2, scale=4)  

set(gca, 'units', 'normalized'); %Just making sure it's normalized
Tight = get(gca, 'TightInset');  %Gives you the bording spacing between plot box and any axis labels
                                 %[Left Bottom Right Top] spacing
NewPos = [Tight(1) Tight(2) 1-Tight(1)-Tight(3) 1-Tight(2)-Tight(4)]; %New plot position [X Y W H]
set(gca, 'Position', NewPos);

ax = gca;
ax.LineWidth = 4;
ax.GridLineWidth = 3;


f3=figure('name','Longitud de onda central vs Temperatura');
plot(TempArray,Lamda_Central,'LineWidth',4,'Color','#00009B');
hold on
plot(20:0.01:60,0.012965774714669*(20:0.01:60)+1546.743406967670,'LineStyle','--','LineWidth',4)
grid on
xlabel('Temperatura [°C]')
ylabel('Longitud de onda [nm]')
title('Longitud de onda central del sensor SSFBG SA1R en función de la temperatura')
grid on
xlim([TempArray(1) TempArray(end)])
legend('Procesamiento experimental','Regresion Lineal')
set(f3,'position',[50,50,Heigth*Aspect_ratio,Heigth])
fontsize(f3, scale=4)  

set(gca, 'units', 'normalized'); %Just making sure it's normalized
Tight = get(gca, 'TightInset');  %Gives you the bording spacing between plot box and any axis labels
                                 %[Left Bottom Right Top] spacing
NewPos = [Tight(1) Tight(2) 1-Tight(1)-Tight(3) 1-Tight(2)-Tight(4)]; %New plot position [X Y W H]
set(gca, 'Position', NewPos);

ax = gca;
ax.LineWidth = 4;
ax.GridLineWidth = 3;


% Regresion Lineal => Lambda=0.012965774714669*T+1546.743406967670


f4=figure('name','Longitud de onda central vs Temperatura');
plot(TempArray,XCP_ratio(:,2),'LineWidth',4,'Color','#00009B');
hold on
grid on
xlabel('Temperatura [°C]')
ylabel('XCP/ACP')
title('XCP/ACP ratio en función de la temperatura')
grid on
xlim([TempArray(1) TempArray(end)])
ylim([0 1])
set(f4,'position',[50,50,Heigth*Aspect_ratio,Heigth])
fontsize(f4, scale=4)  

set(gca, 'units', 'normalized'); %Just making sure it's normalized
Tight = get(gca, 'TightInset');  %Gives you the bording spacing between plot box and any axis labels
                                 %[Left Bottom Right Top] spacing
NewPos = [Tight(1) Tight(2) 1-Tight(1)-Tight(3) 1-Tight(2)-Tight(4)]; %New plot position [X Y W H]
set(gca, 'Position', NewPos);

ax = gca;
ax.LineWidth = 4;
ax.GridLineWidth = 3;


f5=figure('name','Prueba a diferentes temperaturas');
plot(Interrogacion_VCSEL_Mean(:,8,1),Interrogacion_VCSEL_Mean(:,9,1),'LineWidth',4,'Color','#00009B','LineStyle','--');
hold on
plot(Interrogacion_VCSEL_Mean(minimun(1):maximun(1),8,1)+0.3,Ideal_Codes(:,1),'LineWidth',4,'Color','#287233','LineStyle','--');
grid on
xlabel('Longitud de onda [nm]')
ylabel('Reflectividad [u.a]')
title('Interrogación del sensor SSFBG SA1R a diferentes temperaturas')
legend('45°C', '52°C')
grid on
xlim([1546 1548])
set(f5,'position',[50,50,Heigth*Aspect_ratio,Heigth])
fontsize(f5, scale=4)  

set(gca, 'units', 'normalized'); %Just making sure it's normalized
Tight = get(gca, 'TightInset');  %Gives you the bording spacing between plot box and any axis labels
                                 %[Left Bottom Right Top] spacing
NewPos = [Tight(1) Tight(2) 1-Tight(1)-Tight(3) 1-Tight(2)-Tight(4)]; %New plot position [X Y W H]
set(gca, 'Position', NewPos);

ax = gca;
ax.LineWidth = 4;
ax.GridLineWidth = 3;