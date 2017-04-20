import json
import logging
import re

logger = logging.getLogger(__name__)


def Split_CMD(SrcMessage):
    if (SrcMessage.startswith('mcc')):
        if (SrcMessage.startswith('mcc?')):
            return {"cmd":"lst"}
        if (SrcMessage.startswith('mcc+')):
            return {"cmd":"add"}
        if (SrcMessage.startswith('mcc-')):
            return {"cmd":"del"}
        
    if (SrcMessage.startswith('sms:')):
          return {"cmd":"sms"}
        
    return None;


class RtmEventHandler(object):
    def __init__(self, slack_clients, msg_writer):
        self.clients = slack_clients
        self.msg_writer = msg_writer
        self.log = {};

    def handle(self, event):

        if 'type' in event:
            self._handle_by_type(event['type'], event)

    def _handle_by_type(self, event_type, event):
        # See https://api.slack.com/rtm for a full list of events        
        if event_type == 'error':
            # error
            self.msg_writer.write_error(event['channel'], json.dumps(event))
        elif event_type == 'message':
            # message was sent to channel
            self._handle_message(event)
        elif event_type == 'channel_joined':
            # you joined a channel
            self.msg_writer.write_help_message(event['channel'])
        elif event_type == 'group_joined':
            # you joined a private group
            self.msg_writer.write_help_message(event['channel'])
        else:
            pass

    def _handle_message(self, event):
        # Filter out messages from the bot itself, and from non-users (eg. webhooks)
        
        #if event['team'] not in self.log:
        #    self.log[str(event['team'])] ={}
        #self.log[str(event['team'])][str(event['user'])] = event
        
        if ('user' in event) and (not self.clients.is_message_from_me(event['user'])):

            msg_txt = event['text']

            if self.clients.is_bot_mention(msg_txt) or self._is_direct_message(event['channel']):
                # e.g. user typed: "@pybot tell me a joke!"
                MCC = Split_CMD(msg_txt)
                if MCC:
                    self.msg_writer.send_message(event['channel'], 'This is my message! '+json.dumps(MCC))
                elif '?' == msg_txt:
                    self.msg_writer.send_message(event['channel'], json.dumps(event)+'\n'+json.dumps(self.log))
                elif 'help' in msg_txt:
                    self.msg_writer.write_help_message(event['channel'])
                elif re.search('hi|hey|hello|howdy', msg_txt):
                    self.msg_writer.write_greeting(event['channel'], event['user'])
                elif 'joke' in msg_txt:
                    self.msg_writer.write_joke(event['channel'])
                elif 'attachment' in msg_txt:
                    self.msg_writer.demo_attachment(event['channel'])
                elif 'echo' in msg_txt:
                    self.msg_writer.send_message(event['channel'], msg_txt)
                else:
                    self.msg_writer.write_prompt(event['channel'])

    def _is_direct_message(self, channel):
        """Check if channel is a direct message channel

        Args:
            channel (str): Channel in which a message was received
        """
        return channel.startswith('D')
