clc;
clear;

%Constantes
Splitter_40_Atenuacion=-10*log10(48.11/147.2);
Splitter_60_Atenuacion=-10*log10(74/147.2);
Fibra_Optica=0.10055711;
Resistencia_SSFBG=992;
Resistencia_REF=987;


%Datos del laser
VCSEL_mean_Data=importdata('VCSEL_Caract.mat');
VCSEL_Mean_Wavelength=mean(VCSEL_mean_Data(:,3,:),3);


%Importacion de los datos del Fotodiodo SSFBG
Fotodiodo_SSFBG_DATA=zeros(998,4,40); %#1 ->Time, #2 -> Voltaje_VCSEL, #3 -> Power, #4 -> Voltaje
for i=1:40
    Fotodiodo_SSFBG_DATA(:,:,i)=table2array(Fotodiodo_No_Amp('SSFBG\Fotodiodo_FGA01FC_17_11_2023_14h_58m_Temp_VCSEL_T_562_Voltaje_Step_1_Multimeter_OPM'+string(i)+'.csv'));
end


%Importacion de los datos del Fotodiodo de referencia
Fotodiodo_REF_DATA=zeros(998,4,40); %#1 ->Time, #2 -> Voltaje_VCSEL, #3 -> Power, #4 -> Voltaje
for i=1:40
    Fotodiodo_REF_DATA(:,:,i)=table2array(Fotodiodo_No_Amp('REF\Fotodiodo_FGA01FC_17_11_2023_12h_47m_Temp_VCSEL_T_562_Voltaje_Step_1_Multimeter_OPM'+string(i)+'.csv'));
end

%Compensacion de la potencia
Fotodiodo_SSFBG_DATA(:,3,:)=Fotodiodo_SSFBG_DATA(:,3,:)*10^(Splitter_40_Atenuacion/10)*10^-(Splitter_60_Atenuacion/10)*10^-(Fibra_Optica/10);
Fotodiodo_REF_DATA(:,3,:)=Fotodiodo_REF_DATA(:,3,:)*10^(Splitter_40_Atenuacion/10)*10^-(Splitter_60_Atenuacion/10)*10^-(Fibra_Optica/10);

%Conversion de la tension en corriente
Fotodiodo_SSFBG_DATA(:,4,:)=Fotodiodo_SSFBG_DATA(:,4,:)/Resistencia_SSFBG;
Fotodiodo_REF_DATA(:,4,:)=Fotodiodo_REF_DATA(:,4,:)/Resistencia_REF;


%Ajuste de las unidades de las variables
Fotodiodo_SSFBG_DATA(:,3,:)=Fotodiodo_SSFBG_DATA(:,3,:)*10^3;   %mw
Fotodiodo_SSFBG_DATA(:,4,:)=Fotodiodo_SSFBG_DATA(:,4,:)*10^3;   %mA

Fotodiodo_REF_DATA(:,3,:)=Fotodiodo_REF_DATA(:,3,:)*10^3;   %mw
Fotodiodo_REF_DATA(:,4,:)=Fotodiodo_REF_DATA(:,4,:)*10^3;   %mA


f100=figure;
plot(Fotodiodo_SSFBG_DATA(:,3,5),Fotodiodo_SSFBG_DATA(:,4,5));



%Promedio y desviacion estandar de las 40 muestras para cada unidad
Fotodiodo_SSFBG_mean_DATA=zeros(998,4); %#1 ->Time, #2 -> Voltaje_VCSEL, #3 -> Power, #4 -> Voltaje
Fotodiodo_SSFBG_std_DATA=zeros(998,4); %#1 ->Time, #2 -> Voltaje_VCSEL, #3 -> Power, #4 -> Voltaje

Fotodiodo_REF_mean_DATA=zeros(998,4); %#1 ->Time, #2 -> Voltaje_VCSEL, #3 -> Power, #4 -> Voltaje
Fotodiodo_REF_std_DATA=zeros(998,4); %#1 ->Time, #2 -> Voltaje_VCSEL, #3 -> Power, #4 -> Voltaje


for i=1:4
    Fotodiodo_SSFBG_mean_DATA(:,i)=mean(Fotodiodo_SSFBG_DATA(:,i,:),3);
    Fotodiodo_SSFBG_std_DATA(:,i)=std(Fotodiodo_SSFBG_DATA(:,i,:),0,3);

    Fotodiodo_REF_mean_DATA(:,i)=mean(Fotodiodo_REF_DATA(:,i,:),3);
    Fotodiodo_REF_std_DATA(:,i)=std(Fotodiodo_REF_DATA(:,i,:),0,3);
end



%Calculo de la responsividad A/W
Fotodiodo_SSFBG_Responsividad=zeros(998,40);
Fotodiodo_REF_Responsividad=zeros(998,40);

for i=1:40
    Fotodiodo_SSFBG_Responsividad(:,i)=Fotodiodo_SSFBG_DATA(:,4,i)./Fotodiodo_SSFBG_DATA(:,3,i);
    Fotodiodo_REF_Responsividad(:,i)=Fotodiodo_REF_DATA(:,4,i)./Fotodiodo_REF_DATA(:,3,i);

end


Fotodiodo_SSFBG_Responsividad_mean=mean(Fotodiodo_SSFBG_Responsividad,2);
Fotodiodo_SSFBG_Responsividad_std=std(Fotodiodo_SSFBG_Responsividad,0,2);

Fotodiodo_REF_Responsividad_mean=mean(Fotodiodo_REF_Responsividad,2);
Fotodiodo_REF_Responsividad_std=std(Fotodiodo_REF_Responsividad,0,2);


%Corriente fotodetectada maxima
Fotodiodo_SSFBG_Current_max=max(Fotodiodo_SSFBG_mean_DATA(:,4));
Fotodiodo_REF_Current_max=max(Fotodiodo_REF_mean_DATA(:,4));

Fotodiodo_SSFBG_Current_std_geometric=geomean(Fotodiodo_SSFBG_std_DATA(:,4));
Fotodiodo_REF_Current_std_geometric=geomean(Fotodiodo_REF_std_DATA(:,4));





Heigth=1080;
Aspect_ratio=2.76;

f3=figure('Name','Corriente vs Potencia optica');
plot(Fotodiodo_SSFBG_mean_DATA(:,3),Fotodiodo_SSFBG_mean_DATA(:,4),'LineWidth',4,'Color','#00009B')
hold on
plot(Fotodiodo_REF_mean_DATA(:,3),Fotodiodo_REF_mean_DATA(:,4),'LineWidth',4,'Color','#9B111E')
grid on
ylabel('Corriente Fotoeléctrica [mA]')
xlabel('Potencia óptica incidente [mW]')
xlim([min(Fotodiodo_SSFBG_mean_DATA(:,3)) max(Fotodiodo_REF_mean_DATA(:,3))])
%title('Corriente fotoeléctrica promedio en función de la potencia óptica incidente')
grid on
legend('Fotodiodo - SSFBG','Fotodiodo - Referencia')
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



f4=figure('Name','Corriente vs Potencia optica');
plot(Fotodiodo_SSFBG_mean_DATA(:,3),Fotodiodo_SSFBG_std_DATA(:,4),'LineWidth',4,'Color','#00009B','LineStyle','--')
hold on
plot(Fotodiodo_REF_mean_DATA(:,3),Fotodiodo_REF_std_DATA(:,4),'LineWidth',4,'Color','#9B111E','LineStyle','--')
grid on
ylabel('Corriente Fotoeléctrica [mA]')
xlabel('Potencia óptica incidente [mW]')
xlim([min(Fotodiodo_SSFBG_mean_DATA(:,3)) max(Fotodiodo_REF_mean_DATA(:,3))])
%title('Desviación estándar de la corriente fotoeléctrica en función de la potencia óptica incidente')
grid on
legend('Fotodiodo - SSFBG','Fotodiodo - Referencia')
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



f5=figure('Name','Corriente Fotodetectada -  Cajas');
plot(Fotodiodo_SSFBG_mean_DATA(:,3),Fotodiodo_SSFBG_mean_DATA(:,4),'LineWidth',4,'Color','#00009B')
hold on
plot(Fotodiodo_REF_mean_DATA(:,3),Fotodiodo_REF_mean_DATA(:,4),'LineWidth',4,'Color','#9B111E')
plot(Fotodiodo_SSFBG_mean_DATA(:,3),Fotodiodo_SSFBG_std_DATA(:,4),'LineWidth',4,'Color','#00009B','LineStyle','--')
plot(Fotodiodo_REF_mean_DATA(:,3),Fotodiodo_REF_std_DATA(:,4),'LineWidth',4,'Color','#9B111E','LineStyle','--')
grid on
ylabel('Corriente Fotoeléctrica [mA]')
xlabel('Potencia óptica incidente [mW]')
xlim([min(Fotodiodo_SSFBG_mean_DATA(:,3)) max(Fotodiodo_REF_mean_DATA(:,3))])
title('Corriente fotoeléctrica en función de la potencia óptica incidente')
grid on
legend('Fotodiodo SSFBG - Mean','Fotodiodo REF - Mean','Fotodiodo SSFBG - STD','Fotodiodo REF - STD')
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



f6=figure('Name','Responsividad vs Longitud de onda');
plot(VCSEL_Mean_Wavelength,Fotodiodo_SSFBG_Responsividad_mean,'LineWidth',4,'Color','#00009B')
hold on
plot(VCSEL_Mean_Wavelength,Fotodiodo_REF_Responsividad_mean,'LineWidth',4,'Color','#9B111E')
grid on
ylabel('Responsividad [A/W]')
xlabel('Longitud de onda [nm]')
%title('Responsividad promedio en función de la longitud de onda del láser VCSEL')
legend('Fotodiodo - SSFBG','Fotodiodo - Referencia')

grid on
set(f6,'position',[50,50,Heigth*Aspect_ratio,Heigth])
fontsize(f6, scale=4)  
xlim([min(VCSEL_Mean_Wavelength) max(VCSEL_Mean_Wavelength)])
set(gca, 'units', 'normalized'); %Just making sure it's normalized
Tight = get(gca, 'TightInset');  %Gives you the bording spacing between plot box and any axis labels
                                 %[Left Bottom Right Top] spacing
NewPos = [Tight(1) Tight(2) 1-Tight(1)-Tight(3) 1-Tight(2)-Tight(4)]; %New plot position [X Y W H]
set(gca, 'Position', NewPos);
        
ax = gca;
ax.LineWidth = 4;
ax.GridLineWidth = 3;


f7=figure('Name','Responsividad vs Corriente del laser');
plot(VCSEL_Mean_Wavelength,Fotodiodo_SSFBG_Responsividad_std,'LineWidth',4,'Color','#00009B')
hold on
plot(VCSEL_Mean_Wavelength,Fotodiodo_REF_Responsividad_std,'LineWidth',4,'Color','#9B111E')
grid on
ylabel('Responsividad [A/W]')
xlabel('Longitud de onda [nm]')
%title('Desviación estándar de la responsividad en función de la longitud de onda del láser VCSEL')
grid on
legend('Fotodiodo - SSFBG','Fotodiodo - Referencia')

set(f7,'position',[50,50,Heigth*Aspect_ratio,Heigth])
fontsize(f7, scale=4)  
xlim([min(VCSEL_Mean_Wavelength) max(VCSEL_Mean_Wavelength)])
set(gca, 'units', 'normalized'); %Just making sure it's normalized
Tight = get(gca, 'TightInset');  %Gives you the bording spacing between plot box and any axis labels
                                 %[Left Bottom Right Top] spacing
NewPos = [Tight(1) Tight(2) 1-Tight(1)-Tight(3) 1-Tight(2)-Tight(4)]; %New plot position [X Y W H]
set(gca, 'Position', NewPos);

ax = gca;
ax.LineWidth = 4;
ax.GridLineWidth = 3;



f8=figure('Name','Responsividad SSFBG Cajas');
bp1=boxplot(Fotodiodo_SSFBG_Responsividad',VCSEL_Mean_Wavelength,'PlotStyle','traditional');
hold on
grid on
ylabel('Responsividad [A/W]')
xlabel('Longitud de onda [nm]')
title('Responsividad del fotodiodo SSFBG en función de la longitud de onda del láser VCSEL-T')
grid on
set(f8,'position',[50,50,Heigth*Aspect_ratio,Heigth])
fontsize(f8, scale=4)  
xticks(1:100:length(VCSEL_Mean_Wavelength))
xticklabels(round(VCSEL_Mean_Wavelength(length(VCSEL_Mean_Wavelength)-((1:10)-1)*100),2))
set(gca, 'units', 'normalized'); %Just making sure it's normalized
Tight = get(gca, 'TightInset');  %Gives you the bording spacing between plot box and any axis labels
                                 %[Left Bottom Right Top] spacing
NewPos = [Tight(1) Tight(2) 1-Tight(1)-Tight(3) 1-Tight(2)-Tight(4)]; %New plot position [X Y W H]
set(gca, 'Position', NewPos);

set(bp1,'LineWidth',3)
ax = gca;
ax.LineWidth = 4;
ax.GridLineWidth = 3;




f9=figure('Name','Responsividad REF Cajas');
bp2=boxplot(Fotodiodo_REF_Responsividad',VCSEL_Mean_Wavelength,'PlotStyle','traditional');
hold on
grid on
ylabel('Responsividad [A/W]')
xlabel('Longitud de onda [nm]')
title('Responsividad del fotodiodo REF en función de la longitud de onda del láser VCSEL-T')
grid on
set(f9,'position',[50,50,Heigth*Aspect_ratio,Heigth])
fontsize(f9, scale=4)  
xticks(1:100:length(VCSEL_Mean_Wavelength))
xticklabels(round(VCSEL_Mean_Wavelength(length(VCSEL_Mean_Wavelength)-((1:10)-1)*100),2))
set(gca, 'units', 'normalized'); %Just making sure it's normalized
Tight = get(gca, 'TightInset');  %Gives you the bording spacing between plot box and any axis labels
                                 %[Left Bottom Right Top] spacing
NewPos = [Tight(1) Tight(2) 1-Tight(1)-Tight(3) 1-Tight(2)-Tight(4)]; %New plot position [X Y W H]
set(gca, 'Position', NewPos);

set(bp2,'LineWidth',3)
ax = gca;
ax.LineWidth = 4;
ax.GridLineWidth = 3;



