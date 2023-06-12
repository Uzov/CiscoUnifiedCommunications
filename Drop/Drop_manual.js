/**
 * Бета-версия. Макрос исправляет глюк: cбрасывает нежелательную презентацию во время старта H323 звонка, в случае, когда имеет место Interworking.
 * Автор: Юзов Евгений Борисович, ООО "Центр", 12.01.2022.
 */

import xapi from 'xapi';

const DEBUG = true;
const CORRECT_BUTTON_PANELID = 'correctButton' // ID кнопки "Коррекция экрана"

/**
 * Старт локальной презентации, источник - видео с камеры. Потом дожидаемся, пока презентация установится, и сразу же её сбрасываем.
 */
async function StartStopPres() {
  await xapi.Command.Presentation.Start({Instance: '6', PresentationSource: '1', SendingMode: 'LocalRemote'})
  .then(await xapi.Command.Presentation.Stop({Instance: '6', PresentationSource: '1'}))
  .catch(console.log);
  if (DEBUG) {console.log ('Сработал сброс презентации!')}
}

xapi.event.on('UserInterface Extensions Panel Clicked', (event) => {
  if(event.PanelId === CORRECT_BUTTON_PANELID) {StartStopPres();}
  if (DEBUG) {console.log('Correct screen button clicked!')}
});

