
import { createElement, useEffect } from 'react'

const messengerScriptUrl = 'https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1'
const messengerScriptAttribute = 'data-dialogflow-messenger'

function TamarinChat() {
	useEffect(() => {
		if (document.querySelector(`script[${messengerScriptAttribute}]`)) return

		const script = document.createElement('script')
		script.src = messengerScriptUrl
		script.async = true
		script.setAttribute(messengerScriptAttribute, '')
		document.body.appendChild(script)
	}, [])
	

	return createElement('df-messenger', {
		className: 'tamarin-chat-widget',
		intent: 'WELCOME',
		'chat-title': '👩🏻Assistant',
		'agent-id': 'fc90d7a9-03d3-4709-bad9-822bf44bdcd8',
		'language-code': 'en',
	})
}

export default TamarinChat
