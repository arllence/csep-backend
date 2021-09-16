from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    id = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class DocumentSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class DepartmentSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    keyword = serializers.CharField()


class DepartmentFilterSerializer(serializers.Serializer):
    from_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    to_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    department_id = serializers.CharField()


class DepartmentAnalyticSerializer(serializers.Serializer):
    total_documents = serializers.CharField()
    pending_review_documents = serializers.CharField()
    pending_validation_documents = serializers.CharField()
    resubmitted_review_documents = serializers.CharField()
    approved_documents = serializers.CharField()
    rejected_documents = serializers.CharField()
    revoked_documents = serializers.CharField()
    department__name = serializers.CharField()


class DocumentStatusAnalyticSerializer(serializers.Serializer):
    document_status = serializers.CharField()
    total_count = serializers.CharField()
    document__department__name = serializers.CharField()


class UserFilterSerializer(serializers.Serializer):
    from_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    to_date = serializers.DateTimeField(format="YYYY-mm-dd HH:MM:SS")
    department_id = serializers.CharField()
    user_id = serializers.CharField()


class ReportFilterSerializer(serializers.Serializer):
    from_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    to_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")


class ReportAnalyticSerializer(serializers.Serializer):
    document__department__name = serializers.CharField()
    total_documents = serializers.CharField()
    document_status = serializers.CharField()


class DocumentValidationAnalyticSerializer(serializers.Serializer):
    document_status = serializers.CharField()
    total_count = serializers.CharField()
    approved_documents = serializers.CharField()
    rejected_documents = serializers.CharField()
    revoked_documents = serializers.CharField()
    document__department__name = serializers.CharField()
    user__username = serializers.CharField()
    user__first_name = serializers.CharField()
    user__last_name = serializers.CharField()


class DocumentDataClerkAnalyticSerializer(serializers.Serializer):
    document_status = serializers.CharField()
    total_count = serializers.CharField()
    uploaded_documents = serializers.CharField()
    metadata_captured_documents = serializers.CharField()
    resubmitted_documents = serializers.CharField()
    approved_documents = serializers.CharField()
    rejected_documents = serializers.CharField()
    revoked_documents = serializers.CharField()
    document__department__name = serializers.CharField()
    user__username = serializers.CharField()
    user__first_name = serializers.CharField()
    user__last_name = serializers.CharField()

class DocumentDataClerkTAnalyticSerializer(serializers.Serializer):
    document_status = serializers.CharField()
    total_count = serializers.CharField()
    # uploaded_documents = serializers.CharField()
    # metadata_captured_documents = serializers.CharField()
    # resubmitted_documents = serializers.CharField()
    # approved_documents = serializers.CharField()
    # rejected_documents = serializers.CharField()
    # revoked_documents = serializers.CharField()
    document__department__name = serializers.CharField()
    user__username = serializers.CharField()
    user__first_name = serializers.CharField()
    user__last_name = serializers.CharField()
