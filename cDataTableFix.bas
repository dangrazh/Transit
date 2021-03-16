TransposeClassic:
            If m_EnableObjects = True Then
                If IsObject(m_List(y, x)) = True Then
                    Set tempArray(x, y) = m_List(y, x)
                 Else
                    tempArray(x, y) = m_List(y, x)
                End If
             Else
                tempArray(x, y) = m_List(y, x)
            End If
