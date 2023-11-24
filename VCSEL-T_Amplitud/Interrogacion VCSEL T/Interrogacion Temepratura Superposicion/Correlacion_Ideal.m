function [Lambda_Central_corr,Lambda_Central_corr_2,XCP_ratio,Ideal_Codes]=Correlacion_Ideal(Reflectividad_Experimental,Wavelength_Experimental,W_min,W_max,Offset,FWHM_Codes,N,dl,Ma,Orden)
    
    Ml=-(N-1)/2:1:(N-1)/2;
    
    l1 = Wavelength_Experimental(W_min:W_max)';
    l1=l1-(max(l1)+min(l1))/2;
    Ideal_Codes=Generador_Codigos(Offset,FWHM_Codes,N,dl,Ml,Ma,l1,Orden);
    [~,wavelengt_center_Ideal_Code]=find(l1>=0);
    wavelengt_center_Ideal_Code=wavelengt_center_Ideal_Code(end);

    max_R_Experimental=max(Reflectividad_Experimental(W_min:W_max));
    Ideal_Codes=Ideal_Codes*max_R_Experimental/max(Ideal_Codes);
    [Correlacion,indice_Correlacion] = xcorr(Reflectividad_Experimental(W_min:W_max),Ideal_Codes);
    Correlacion=Correlacion/max(Correlacion);
    

    [~,Lambda_Max_ACP_Index]=max(Correlacion);
    %Lambda_Central_corr=Wavelength_Experimental(W_max/2+indice_Correlacion(Lambda_Max_ACP_Index));
    [max_acp_xcp,max_index_Acp_xcp]=findpeaks(Correlacion,indice_Correlacion,'Npeaks',2,'SortStr','descend');
    Lambda_Central_corr=Wavelength_Experimental(W_min+wavelengt_center_Ideal_Code+max_index_Acp_xcp(1));
    Lambda_Central_corr_2=Wavelength_Experimental(W_min+wavelengt_center_Ideal_Code+max_index_Acp_xcp(2));

    XCP_ratio=zeros(1,2);

    if length(max_acp_xcp)==1
        XCP_ratio(XCP_ratio>=0)=1;
       
    else
        XCP_ratio=max_acp_xcp;
    end


   

end

