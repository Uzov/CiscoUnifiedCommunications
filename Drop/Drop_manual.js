/**
�*�����-������.���������������������:�c�������������������������������������������������H323�������,��������,����������������Interworking.
�*������:���������������������,���Π"�����",�12.01.2022.
�*/

import�xapi�from�'xapi';

const�DEBUG�=�true;
const�CORRECT_BUTTON_PANELID�=�'correctButton'�//�ID�������"����������������"

/**
�*��������������������������,���������-�������������.����������������,����������������������������,���������帠����������.
�*/
async�function�StartStopPres()�{
��await�xapi.Command.Presentation.Start({Instance:�'6',�PresentationSource:�'1',�SendingMode:�'LocalRemote'})
��.then(await�xapi.Command.Presentation.Stop({Instance:�'6',�PresentationSource:�'1'}))
��.catch(console.log);
��if�(DEBUG)�{console.log�('������������������������!')}
}

xapi.event.on('UserInterface�Extensions�Panel�Clicked',�(event)�=>�{
��if(event.PanelId�===�CORRECT_BUTTON_PANELID)�{StartStopPres();}
��if�(DEBUG)�{console.log('Correct�screen�button�clicked!')}
});

