import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from Admin.models import tbl_message, tbl_property, tbl_newuser
from django.utils import timezone
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.property_id = self.scope['url_route']['kwargs']['property_id']
        self.room_group_name = f"chat_{self.user_id}_{self.property_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            # Handle different message types
            if data.get('type') == 'load_history':
                await self.load_chat_history()
                return
            elif data.get('type') == 'mark_read':
                await self.mark_messages_as_read(self.user_id, self.property_id)
                return
            elif data.get('type') == 'mark_message_read':
                message_id = data.get('message_id')
                await self.mark_single_message_as_read(message_id)
                return
            
            message = data.get('message', '').strip()
            sender = data.get('sender', 'user')
            
            if not message:
                await self.send(text_data=json.dumps({
                    'error': 'Message cannot be empty'
                }))
                return
            
            # Validate message length (different limits for admin and user)
            max_length = 1000 if sender == 'admin' else 500
            if len(message) > max_length:
                await self.send(text_data=json.dumps({
                    'error': f'Message too long (max {max_length} characters)'
                }))
                return
            
            # Get user and property objects
            user_obj = await self.get_user(self.user_id)
            property_obj = await self.get_property(self.property_id)
            
            if not user_obj:
                await self.send(text_data=json.dumps({
                    'error': 'User not found'
                }))
                return
                
            if not property_obj:
                await self.send(text_data=json.dumps({
                    'error': 'Property not found'
                }))
                return

            # Save message to database
            message_obj = await self.save_message(
                sender_obj=user_obj,
                property_obj=property_obj,
                message=message,
                is_from_admin=(sender == "admin")
            )
            # If admin sent a message, mark user's pending messages as replied
            if sender == "admin":
                await self.mark_pending_messages_as_replied(self.user_id, self.property_id)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender,
                    'timestamp': message_obj.created_at.isoformat() if message_obj else timezone.now().isoformat(),
                    'message_id': message_obj.id if message_obj else None
                }
            )
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f'Error processing message: {str(e)}'
            }))

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event.get('timestamp'),
            'message_id': event.get('message_id')
        }))
        
    async def load_chat_history(self):
        """Load and send chat history for this user and property"""
        try:
            messages = await self.get_chat_history(self.user_id, self.property_id)
            
            # Format messages for frontend
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    'message': msg.body,
                    'sender': 'admin' if msg.is_from_admin else 'user',
                    'timestamp': msg.created_at.isoformat(),
                    'message_id': msg.id
                })
            
            await self.send(text_data=json.dumps({
                'type': 'chat_history',
                'messages': formatted_messages
            }))
            
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f'Error loading chat history: {str(e)}'
            }))

    # Database operations using database_sync_to_async
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return tbl_newuser.objects.get(id=user_id)
        except tbl_newuser.DoesNotExist:
            return None

    @database_sync_to_async
    def get_property(self, property_id):
        try:
            return tbl_property.objects.get(id=property_id)
        except tbl_property.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, sender_obj, property_obj, message, is_from_admin=False):
        try:
            return tbl_message.objects.create(
                sender=sender_obj,
                property=property_obj,
                is_from_admin=is_from_admin,
                body=message,
                status="replied" if is_from_admin else "pending",
                is_read=False
            )
        except Exception as e:
            print(f"Error saving message: {e}")
            return None

    @database_sync_to_async
    def get_chat_history(self, user_id, property_id, limit=50):
        try:
            return list(
                tbl_message.objects.filter(
                    sender_id=user_id,
                    property_id=property_id
                ).order_by('created_at')[:limit]
            )
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []

    @database_sync_to_async
    def mark_messages_as_read(self, user_id, property_id):
        """Mark messages as read (useful for admin interface)"""
        try:
            tbl_message.objects.filter(
                sender_id=user_id,
                property_id=property_id,
                is_read=False
            ).update(is_read=True)
        except Exception as e:
            print(f"Error marking messages as read: {e}")

    @database_sync_to_async
    def mark_pending_messages_as_replied(self, user_id, property_id):
        try:
            tbl_message.objects.filter(
                sender_id=user_id,
                property_id=property_id,
                is_from_admin=False,
                status="pending"
            ).update(status="replied")
        except Exception as e:
            print(f"Error updating pending messages: {e}")        

    @database_sync_to_async
    def mark_single_message_as_read(self, message_id):
        try:
            tbl_message.objects.filter(id=message_id, is_read=False).update(is_read=True)
        except Exception as e:
            print(f"Error marking message {message_id} as read: {e}")
