/**
 * Áåòà-âåðñèÿ. Ìàêðîñ èñïðàâëÿåò ãëþê: cáðàñûâàåò íåæåëàòåëüíóþ ïðåçåíòàöèþ âî âðåìÿ ñòàðòà H323 çâîíêà, â ñëó÷àå, êîãäà èìååò ìåñòî Interworking.
 * Àâòîð: Þçîâ Åâãåíèé Áîðèñîâè÷, ÎÎÎ "Öåíòð", 12.01.2022.
 */

import xapi from 'xapi';

const DEBUG = true;
const CORRECT_BUTTON_PANELID = 'correctButton' // ID êíîïêè "Êîððåêöèÿ ýêðàíà"

/**
 * Ñòàðò ëîêàëüíîé ïðåçåíòàöèè, èñòî÷íèê - âèäåî ñ êàìåðû. Ïîòîì äîæèäàåìñÿ, ïîêà ïðåçåíòàöèÿ óñòàíîâèòñÿ, è ñðàçó æå å¸ ñáðàñûâàåì.
 */
async function StartStopPres() {
  await xapi.Command.Presentation.Start({Instance: '6', PresentationSource: '1', SendingMode: 'LocalRemote'})
  .then(await xapi.Command.Presentation.Stop({Instance: '6', PresentationSource: '1'}))
  .catch(console.log);
  if (DEBUG) {console.log ('Ñðàáîòàë ñáðîñ ïðåçåíòàöèè!')}
}

xapi.event.on('UserInterface Extensions Panel Clicked', (event) => {
  if(event.PanelId === CORRECT_BUTTON_PANELID) {StartStopPres();}
  if (DEBUG) {console.log('Correct screen button clicked!')}
});

