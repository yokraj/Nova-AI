import { SwarmMessage, SwarmMessageType } from '../types/swarm';

export class SwarmCommunicator {
  private messageHistory: SwarmMessage[] = [];

  sendMessage(
    senderAgentId: string,
    senderAgentName: string,
    type: SwarmMessageType,
    content: string,
    receiverAgentId?: string,
    payload?: any
  ): SwarmMessage {
    const msg: SwarmMessage = {
      messageId: `msg-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
      timestamp: new Date().toISOString(),
      senderAgentId,
      senderAgentName,
      receiverAgentId,
      type,
      content,
      payload,
    };
    this.messageHistory.push(msg);
    return msg;
  }

  getMessages(): SwarmMessage[] {
    return [...this.messageHistory];
  }
}
