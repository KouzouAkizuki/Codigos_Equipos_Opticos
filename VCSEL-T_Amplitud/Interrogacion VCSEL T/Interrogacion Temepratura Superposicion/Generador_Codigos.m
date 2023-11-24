
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%% Daniel Pastor & Andrés Triana, Valencia 6/10/2014 %%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function espectro=Generador_Codigos(Offset,FWHM,N,dl,Ml,Ma,ll,Orden)

espectro=zeros(1,length(ll));                   

    for m=1:1:N
        espectro = espectro + Ma(1,m)*(exp(-((ll-Ml(1,m)*dl-Offset(1))/(FWHM/sqrt(4*log(2)))).^(2*Orden)));
    end

end