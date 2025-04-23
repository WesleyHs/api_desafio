from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import bancoApi
from .serializers import DesafioSerializer
from datetime import datetime

class uploadView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            if 'file' not in request.FILES:
                return Response({'mensagem': 'Nenhum arquivo localizado'}, status=status.HTTP_400_BAD_REQUEST)
            
            file = request.FILES['file']
            content = file.read().decode('utf-8').splitlines()
            
            results = {}
            
            for line in content:
                user_id = int(line[0:10].strip())
                name = line[10:55].strip()
                order_id = int(line[55:65].strip())
                product_id = int(line[65:75].strip())
                value = float(line[75:87].strip())
                date = line[-8:].strip()
                
                if user_id not in results:
                    results[user_id] = {
                        'user_id': user_id,
                        'name': name,
                        'orders': {}
                    }
                
                if order_id not in results[user_id]['orders']:
                    results[user_id]['orders'][order_id] = {
                        'order_id': order_id,
                        'total': 0,
                        'date': datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d'),
                        'products': []
                    }
                
                product = {
                    'product_id': product_id,
                    'value': f"{value:.2f}"
                }
                results[user_id]['orders'][order_id]['products'].append(product)
                results[user_id]['orders'][order_id]['total'] += value
            
            final_results = []
            for user_data in results.values():
                user_data['orders'] = list(user_data['orders'].values())
                for order in user_data['orders']:
                    order['total'] = f"{order['total']:.2f}"
                final_results.append(user_data)
            
            for result in final_results:
                serializer = DesafioSerializer(data=result)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(final_results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erro': str(e), 'mensagem': 'Erro ao carregar arquivo'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)