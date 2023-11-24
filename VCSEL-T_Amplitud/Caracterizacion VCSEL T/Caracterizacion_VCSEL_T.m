clear;
clc;

%Constantes
Splitter_40_Atenuacion=-10*log10(48.11/147.2);
Splitter_60_Atenuacion=-10*log10(74/147.2);

Interrogacion_VCSEL_T=zeros(998,4,5); %#1 ->Time, #2 -> Voltaje Ideal, #3 -> Wavelength, #4 -> Power
for i=1:5
    Interrogacion_VCSEL_T(:,:,i)=table2array(VCSEL_T('VCSEL_1550_T_Caracterizacion_15_11_2023_Temp_562_Voltaje_Step_1_OPM_OSA_'+string(i)+'_muestra.csv'));
end

Interrogacion_VCSEL_T(:,4,:)=Interrogacion_VCSEL_T(:,4,:)*10^(Splitter_60_Atenuacion/10)*10^3;
Interrogacion_VCSEL_T(:,2,:)=Interrogacion_VCSEL_T(:,2,:)*-18./max(Interrogacion_VCSEL_T(:,2,:));
Interrogacion_VCSEL_T(:,3,:)=Interrogacion_VCSEL_T(:,3,:)*10^9;


Mean_Wavelength=mean(Interrogacion_VCSEL_T(:,3,:),3);
Mean_Power=mean(Interrogacion_VCSEL_T(:,4,:),3);
max_power=max(Mean_Power);
max_wavelength=max(Mean_Wavelength);
min_wavelength=min(Mean_Wavelength);

STD_Wavelength=std(Interrogacion_VCSEL_T(:,3,:),1,3);
STD_Power=std(Interrogacion_VCSEL_T(:,4,:),1,3);

Wavelength_Resolution=-mean(diff(Mean_Wavelength))*10^3;

STD_Wavelength_Geomean=geomean(STD_Wavelength);
STD_Power_Geomean=geomean(STD_Power);


Heigth=1080;
Aspect_ratio=2.76;


f1=figure('Name','Potencia Optica Media');
plot(Interrogacion_VCSEL_T(:,2,1),Mean_Power);

f2=figure('Name','Potencia Optica STD');
plot(Interrogacion_VCSEL_T(:,2,1),STD_Power);


f3=figure('Name','Potencia Cajas');
bp1=boxplot(squeeze(Interrogacion_VCSEL_T(:,4,:))',Interrogacion_VCSEL_T(:,2,1),'PlotStyle','traditional');
hold on
grid on
xlabel('Tensión [V]')
ylabel('Potencia Óptica [\mu W]')
title('Potencia óptica del láser VCSEL-T a 20°C')
xticks(1:100:length(Interrogacion_VCSEL_T(:,2,1)))
xticklabels(round(Interrogacion_VCSEL_T(length(Interrogacion_VCSEL_T(:,2,1))-((1:10)-1)*100,2,1),2))
grid on
set(f3,'position',[50,50,Heigth*Aspect_ratio,Heigth])
fontsize(f3, scale=4)  

%xlim([min(VCSEL_mean_DATA(:,3)) max(VCSEL_mean_DATA(:,3))])

set(gca, 'units', 'normalized'); %Just making sure it's normalized
Tight = get(gca, 'TightInset');  %Gives you the bording spacing between plot box and any axis labels
                                 %[Left Bottom Right Top] spacing
NewPos = [Tight(1) Tight(2) 1-Tight(1)-Tight(3) 1-Tight(2)-Tight(4)]; %New plot position [X Y W H]
set(gca, 'Position', NewPos);

set(bp1,'LineWidth',3)
ax = gca;
ax.LineWidth = 4;
ax.GridLineWidth = 3;
%lambda=-1.175692512846067*10^(-5)*V^3-0.027479643004984*v^2+0.043730257712403*v+1549.473640641302

f4=figure('Name','Longitud de onda Media');
plot(Interrogacion_VCSEL_T(1:(end-20),2,1),Mean_Wavelength(1:(end-20)));

f5=figure('Name','Longitud de onda STD');
plot(Interrogacion_VCSEL_T(:,2,1),STD_Wavelength);



f8=figure('Name','Potencia Cajas');
bp2=boxplot(squeeze(Interrogacion_VCSEL_T(:,3,:))',Interrogacion_VCSEL_T(:,2,1),'PlotStyle','traditional');
hold on
grid on
xlabel('Tensión [V]')
ylabel('Longitud de onda [nm]')
title('Longitud de onda del láser VCSEL-T a 20°C')
xticks(1:100:length(Interrogacion_VCSEL_T(:,2,1)))
xticklabels(round(Interrogacion_VCSEL_T(length(Interrogacion_VCSEL_T(:,2,1))-((1:10)-1)*100,2,1),2))
grid on
set(f8,'position',[50,50,Heigth*Aspect_ratio,Heigth])
fontsize(f8, scale=4)  

%xlim([min(VCSEL_mean_DATA(:,3)) max(VCSEL_mean_DATA(:,3))])

set(gca, 'units', 'normalized'); %Just making sure it's normalized
Tight = get(gca, 'TightInset');  %Gives you the bording spacing between plot box and any axis labels
                                 %[Left Bottom Right Top] spacing
NewPos = [Tight(1) Tight(2) 1-Tight(1)-Tight(3) 1-Tight(2)-Tight(4)]; %New plot position [X Y W H]
set(gca, 'Position', NewPos);

set(bp2,'LineWidth',3)
ax = gca;
ax.LineWidth = 4;
ax.GridLineWidth = 3;



